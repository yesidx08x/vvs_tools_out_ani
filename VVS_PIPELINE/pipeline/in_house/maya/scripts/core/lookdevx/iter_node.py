import ufe
import pymel.core as pm

def traverse_materialx_stack(root_node):
    if not pm.objExists(root_node):
        print(f"错误: 节点 {root_node} 不存在")
        return

    # 转换为 UFE 路径
    ufe_path = ufe.PathString.path(root_node)

    scene_item = ufe.Hierarchy.createItem(ufe_path)
    if not scene_item:
        print(f"错误: 无法创建 {root_node} 的 UFE 场景项")
        return

    # 开始遍历
    print(f"遍历 MaterialXStack1 层级:")
    traverse_ufe_hierarchy(scene_item)

def traverse_ufe_hierarchy(item, depth=0):

    """递归遍历 UFE 子节点"""
    node_path = ufe.PathString.string(item.path())
    node_name = item.nodeName()
    node_type = item.nodeType()
    indent = "  " * depth
    print(f"{indent}├─ {node_name} ({node_type}) [路径: {node_path}]")

    # 获取子节点
    hierarchy = ufe.Hierarchy.hierarchy(item)
    if hierarchy:
        for child in hierarchy.children():
            traverse_ufe_hierarchy(child, depth + 1)

def main():
    selects=pm.ls(selection=True)
    for select in selects:
        #|materialXStack1|materialXStackShape1
        print(select)


    traverse_materialx_stack("|materialXStack1|materialXStackShape1")