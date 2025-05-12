import copy
class ExplorationTree:
    """
    为一次自动化测试构造路径树
    """
    def __init__(self, root_activity):
        self.root = {
            "activity": root_activity,
            "children": [],  # 子节点列表
            "inefficient_events": [], #未触发跳转的事件
            "transition_events": []  # 触发跳转的事件（如按钮点击）
        }
        self.current_path = []  # 记录当前路径

    def add_node(self, parent_activity, new_activity, event_desc):
        """
        添加新节点到树中
        :param parent_activity: 父节点活动名
        :param new_activity: 新活动名
        :param event_desc: 触发跳转的事件描述
        """

        # 检查new_activity是否已经存在于树中
        def _check_exists(node, target_activity):
            if node["activity"] == target_activity:
                return True
            for child in node["children"]:
                if _check_exists(child, target_activity):
                    return True
            return False

        # 如果new_activity已经存在，直接返回
        if _check_exists(self.root, new_activity):
            return

        def _add(node):
            # 如果没有真正的根节点，将当前活动设置为真正的根节点
            if node["activity"] == "Launcher" and node["children"] == []:
                node["children"].append({
                    "activity": new_activity,
                    "children": [],
                    "inefficient_events": [],
                    "transition_events": [event_desc]
                })
                print("successfully added root child!")
                return True

            # 找到父节点
            if node["activity"] == parent_activity:
                # 检查是否已存在该子节点
                for child in node["children"]:
                    if child["activity"] == new_activity:
                        # 如果子节点已存在，添加新的事件描述（如果有）
                        if event_desc not in child["transition_events"]:
                            child["transition_events"].append(event_desc)
                            print("added new transition event to existing node")
                        return False

                # 不存在则添加新节点
                node["children"].append({
                    "activity": new_activity,
                    "children": [],
                    "transition_events": [event_desc],
                    "inefficient_events": []
                })
                print("successfully added new child node!")
                return True

            # 递归搜索
            for child in node["children"]:
                if _add(child):
                    return True
            return False

        _add(self.root)

    def add_inefficient_event(self, from_activity, event_desc):
        def dfs(node):
            if node["activity"] == from_activity:
                node["inefficient_events"].append(event_desc)
                return True
            for child in node["children"]:
                if dfs(child):
                    return True
            return False
        if not dfs(self.root):
            self.root["children"].append(
                {"activity": from_activity,
                 "children": [],
                 "transition_events": [event_desc],
                 "inefficient_events": []})


    def save_to_json(self, file_path):
        """保存树结构到JSON文件"""
        import json
        with open(file_path, 'w') as f:
            # 设置缩进
            json.dump(self.root, f, indent=2)

    @staticmethod
    def compare_trees(tree1_path, tree2_path):
        import json
        # from collections import Counter

        def load_tree(file_path):
            with open(file_path) as f:
                return json.load(f)

        def analyze_tree(node, metrics):
            # 统计节点总数
            metrics['node_count'] += 1
            # 统计分支因子总数
            metrics['branching_factors'].append(len(node["children"]))
            # 统计无效事件总数
            metrics['inefficient_events'] += len(node["inefficient_events"])
            # 记录最深路径长度
            if not node["children"]:
                metrics['max_depth'] = max(metrics['max_depth'], metrics['current_depth'])
            else:
                metrics['current_depth'] += 1
                for child in node["children"]:
                    analyze_tree(child, metrics)
                metrics['current_depth'] -= 1

        # 加载树
        tree1 = load_tree(tree1_path)
        tree2 = load_tree(tree2_path)

        # 分析树
        metrics1 = {'node_count': 0, 'activities': set(), 'branching_factors': [], 'max_depth': 0, 'current_depth': 0, 'inefficient_events': 0}
        metrics2 = copy.deepcopy(metrics1)
        analyze_tree(tree1, metrics1)
        analyze_tree(tree2, metrics2)

        # 输出结果
        print("<===== Tree1 指标 =====>")
        print(f"总节点数: {metrics1['node_count']}")
        print(f"平均分支因子: {sum(metrics1['branching_factors']) / len(metrics1['branching_factors']):.2f}")
        print(f"最大深度: {metrics1['max_depth']}\n")
        print(f"平均无效事件数: {(metrics1['inefficient_events'] / metrics1['node_count']):.2f}")

        print("<===== Tree2 指标 =====>")
        print(f"总节点数: {metrics2['node_count']}")
        print(f"平均分支因子: {sum(metrics2['branching_factors']) / len(metrics2['branching_factors']):.2f}")
        print(f"最大深度: {metrics2['max_depth']}\n")
        print(f"平均无效事件数: {(metrics2['inefficient_events'] / metrics2['node_count']):.2f}")

        # 对比唯一活动差异
        diff1 = metrics1['activities'] - metrics2['activities']
        diff2 = metrics2['activities'] - metrics1['activities']
        print(f"Tree1 独有活动: {diff1 if diff1 else '无'}")
        print(f"Tree2 独有活动: {diff2 if diff2 else '无'}")