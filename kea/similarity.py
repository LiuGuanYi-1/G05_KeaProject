import logging
import os
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from collections import deque
from concurrent.futures import ThreadPoolExecutor
import pytesseract

# 默认相似度阈值
THREGHOLD = 0.85

class Similarity(object):
    def __init__(self, sim_k):
        """
        初始化相似度计算器
        :param sim_k: 连续相似次数阈值
        """
        self.sim_k = sim_k
        self.sim_count = 0
        self.THREGHOLD = THREGHOLD
        self.logger = logging.getLogger('SimilarityCalculator')

    def detected_ui_tarpit(self, input_manager):
        """
        检测UI陷阱
        :param input_manager: 输入管理器实例
        :return: 是否检测到UI陷阱
        """
        last_state = input_manager.policy.get_last_state()
        last_state_screen = last_state.get_state_screen()
        current_state = input_manager.device.get_current_state()
        current_state_screen = current_state.get_state_screen()

        # 计算相似度
        sim_score = self.calculate_similarity(last_state_screen, current_state_screen)

        self.logger.info(f'Similarity score: {sim_score}')
        if sim_score < self.THREGHOLD:
            self.sim_count = 0
        else:
            self.sim_count += 1

        return self.sim_count >= self.sim_k

    @staticmethod
    def dhash(image, hash_size=8):
        """
        计算图像的差异哈希（dHash）
        :param image: 输入图像
        :param hash_size: 哈希大小
        :return: 哈希值
        """
        resized = cv2.resize(image, (hash_size + 1, hash_size), interpolation=cv2.INTER_LINEAR)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        diff = gray[:, 1:] > gray[:, :-1]
        return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])

    @staticmethod
    def phash(image, hash_size=32):
        """
        计算图像的感知哈希（pHash）
        :param image: 输入图像
        :param hash_size: 哈希大小
        :return: 哈希值
        """
        resized = cv2.resize(image, (hash_size, hash_size), interpolation=cv2.INTER_LINEAR)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        dct = cv2.dct(np.float32(gray))
        dct_roi = dct[:8, :8]  # 取低频部分
        avg = np.mean(dct_roi)
        hash_val = (dct_roi > avg).flatten()
        return sum([2 ** i for (i, v) in enumerate(hash_val) if v])

    @staticmethod
    def hamming_distance(hash1, hash2):
        """
        计算两个哈希值之间的汉明距离
        :param hash1: 第一个哈希值
        :param hash2: 第二个哈希值
        :return: 汉明距离
        """
        return bin(hash1 ^ hash2).count("1")

    @staticmethod
    def calculate_ssim(fileA, fileB):
        """
        计算两个图像的结构相似性（SSIM）
        :param fileA: 第一个图像文件路径
        :param fileB: 第二个图像文件路径
        :return: SSIM得分
        """
        imgA = cv2.imread(fileA)
        imgB = cv2.imread(fileB)
        grayA = cv2.cvtColor(imgA, cv2.COLOR_BGR2GRAY)
        grayB = cv2.cvtColor(imgB, cv2.COLOR_BGR2GRAY)
        return ssim(grayA, grayB)

    @staticmethod
    def extract_text(image):
        """
        使用OCR提取图像中的文本
        :param image: 输入图像
        :return: 提取的文本
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)
        return text.strip()

    def calculate_similarity(self, fileA, fileB):
        """
        计算两个图像文件的相似度得分
        :param fileA: 第一个图像文件路径
        :param fileB: 第二个图像文件路径
        :return: 相似度得分
        """

        imgA = cv2.imread(fileA)
        imgB = cv2.imread(fileB)
        # 不足两个图片直接返回
        if imgA is None or imgB is None:
            return 0.0

        # 检查尺寸是否相同
        if imgA.shape != imgB.shape:
            return 0.0

        # 并行计算哈希值
        with ThreadPoolExecutor() as executor:
            future_dhashA = executor.submit(self.dhash, imgA)
            future_dhashB = executor.submit(self.dhash, imgB)
            future_phashA = executor.submit(self.phash, imgA)
            future_phashB = executor.submit(self.phash, imgB)
            dhashA, dhashB = future_dhashA.result(), future_dhashB.result()
            phashA, phashB = future_phashA.result(), future_phashB.result()

        # 计算哈希相似度
        dhash_score = 1 - self. hamming_distance(dhashA, dhashB) / 64.0
        phash_score = 1 - self.hamming_distance(phashA, phashB) / 64.0
        dhash_score = np.power(dhash_score, 2)
        phash_score = np.power(phash_score, 2)

        # 计算SSIM
        ssim_score = self.calculate_ssim(fileA, fileB)

        # 设置权重，统计综合得分
        similarity_score = 0.3 * dhash_score + 0.3 * phash_score + 0.4 * ssim_score

        # OCR文本比对
        textA = self.extract_text(imgA)
        textB = self.extract_text(imgB)
        if textA == textB:
            similarity_score = min(1.0, similarity_score + 0.1)  # 文本相同则增加相似度

        return similarity_score