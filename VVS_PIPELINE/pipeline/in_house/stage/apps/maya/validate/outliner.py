import maya.api.OpenMaya as om
from maya import cmds

from stage.apps.validate_core import ValidateCore


class Outliner(ValidateCore):
    nice_name = "大纲"

    def __init__(self):
        super().__init__()
        self.autofixable = False
        self.ignorable = False
        self.selectable = True

        self.missing_nodes = []
        self.extra_nodes = []

    def collect(self):
        pass

    def validate(self,parameter):
        if not parameter:
            return
        self.missing_nodes = []
        self.extra_nodes = []

        top_nodes=list(parameter.keys())
        def recurse_check(parent_path, structure_dict):
            expected_children = structure_dict.keys()
            if not cmds.objExists(parent_path):
                self.missing_nodes.append(parent_path)
                return

            # 获取实际存在的 transform 子节点
            actual_children = cmds.listRelatives(parent_path, children=True, type='transform') or []

            # 如果这是“末尾层级”节点（结构 dict 是空的），就不再检查其子项
            if not structure_dict:
                return

            # 检查多余的子节点（仅限中间层级）
            for actual in actual_children:
                if actual not in expected_children:
                    self.extra_nodes.append(f"{parent_path}|{actual}")

            # 递归检查定义中的子节点
            for expected in expected_children:
                full_path = f"{parent_path}|{expected}"
                if not cmds.objExists(full_path):
                    self.missing_nodes.append(full_path)
                elif isinstance(structure_dict[expected], dict):
                    recurse_check(full_path, structure_dict[expected])


        all_roots = cmds.ls(assemblies=True)
        for node in  top_nodes:
            if node not in all_roots:
                self.missing_nodes.append(node)



        other_roots = [r for r in all_roots if r not in  top_nodes and r not in ['persp', 'top', 'front', 'side']]

        if other_roots:
            self.extra_nodes=self.extra_nodes+other_roots
            self.failed(msg=f"存在非根节点: {other_roots}")
            print("⚠️ 警告：存在非 %s 根节点："%top_nodes, other_roots)

        # 递归检查结构
        for node in top_nodes:
            recurse_check(node, parameter[node])


        if self.missing_nodes:
            self.failed(msg=f"缺失节点: {self.missing_nodes}")
            print("❌ 缺失节点：")
            for node in self.missing_nodes:
                print(" -", node)

        if self.extra_nodes:
            self.failed(msg=f"非法层级节点: {self.extra_nodes}")
            print("❌ 非法层级节点：")
            for node in self.extra_nodes:
                print(" -", node)

        if not self.missing_nodes and not self.extra_nodes:
            self.passed()

    def select(self):
        cmds.select(self.missing_nodes+self.extra_nodes)
