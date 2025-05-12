from PathVariaty import ExplorationTree

class ExplorationTreeComparator:
    """
    用于比较两棵探索树的工具类
    """
    
    def __init__(self, tree1_path: str, tree2_path: str):
        """
        初始化比较器
        :param tree1_path: 第一棵树JSON文件路径
        :param tree2_path: 第二棵树JSON文件路径
        """
        self.tree1_path = tree1_path
        self.tree2_path = tree2_path
        self.exploration_tree = ExplorationTree("Launcher")  # 创建临时实例用于调用比较方法
    
    def compare_trees(self):
        """
        执行树比较并返回结果字典
        :return: 包含比较结果的字典
        """
        # 调用PathVariaty中的比较方法
        self.exploration_tree.compare_trees(self.tree1_path, self.tree2_path)
        
        # 返回更结构化的结果
        return self._get_structured_comparison()
    
    def _get_structured_comparison(self):
        """
        获取结构化的比较结果
        :return: 包含各项指标的字典
        """
        # 这里可以添加更详细的结构化结果处理
        # 当前直接使用PathVariaty中的打印输出
        
        # 返回示例结构（实际实现需要修改PathVariaty.compare_trees方法以返回数据）
        return {
            "message": "Comparison completed. See console output for details.",
            "tree1_path": self.tree1_path,
            "tree2_path": self.tree2_path
        }
    
    def save_comparison_report(self, output_path: str):
        """
        保存比较报告到文件
        :param output_path: 输出文件路径
        """
        import io
        from contextlib import redirect_stdout
        
        # 捕获控制台输出
        with io.StringIO() as buf, redirect_stdout(buf):
            self.compare_trees()
            report_content = buf.getvalue()
        
        # 写入文件
        with open(output_path, 'w') as f:
            f.write(report_content)
        
        print(f"Comparison report saved to: {output_path}")


# 使用示例
if __name__ == "__main__":
    # 创建比较器实例
    comparator = ExplorationTreeComparator(
        "E:\\Kea-main\\Kea-main\\activitytree\\Myexpenses\\exploration_tree_1265llm.json",
        "E:\\Kea-main\\Kea-main\\activitytree\\Myexpenses\\exploration_tree_6001llm.json"
    )
    
    # 执行比较
    comparator.compare_trees()
    
    # 保存比较报告
    comparator.save_comparison_report("comparison_report.txt")