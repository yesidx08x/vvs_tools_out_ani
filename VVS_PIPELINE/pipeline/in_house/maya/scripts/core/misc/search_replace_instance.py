import os
import re
import pymel.core as pm
import maya.OpenMaya as om

props_directory = r'R:\1023_TLD\ProductionFolder\FromClient\20240521_CSM_TO01\scans\cesiumContainerArea\assets\props'


def find_asset(asset_name):
    for root, dirs, files in os.walk(props_directory):
        if 'maya' in root:
            for f in files:
                if re.findall(r'%s.*' % asset_name, f, re.I):
                    print(os.path.join(root, f))
                    return os.path.join(root, f)


def path_2_dag_node(full_path):
    if not pm.objExists(full_path):
        return None
    else:
        selectionList = om.MSelectionList()
        selectionList.add(full_path)
        dag_path = om.MDagPath()
        selectionList.getDagPath(0, dag_path)
        return dag_path.isInstanced()


def traverse_hierarchy(path):
    children = pm.listRelatives(path, children=True, fullPath=True) or []
    for child in children:
        yield child
        for sub_child in traverse_hierarchy(child):
            yield sub_child


selects = pm.ls(sl=1)
asset_name_list = []

for node in selects:
    master_grp = None
    for child in traverse_hierarchy(node):
        is_instanced = path_2_dag_node(child)
        shape = pm.listRelatives(child, children=True, fullPath=True) or []

        if shape and not shape[0].nodeType() == 'UnknownDag':
            continue
        asset_node = child.getParent()
        if re.findall(r'_A_|_B_|_C_|_D_|_E_', asset_node.name()):
            asset_nams = asset_node.name().split('_')
            asset_name = asset_nams[0] + '_' + asset_nams[1]
        else:
            asset_name = asset_node.name().split('_')[0]
        print(asset_name)

        if asset_name not in asset_name_list:
            asset_name_list.append(asset_name)
            asset_file = find_asset(asset_name)
            results = pm.importFile(asset_file, returnNewNodes=1)
            for ret_node in results:
                if re.match(r'master$|\|master$', ret_node.name(), re.I):
                    master_grp = ret_node
                    pm.parent(master_grp, asset_node, r=1)
                    break
        else:
            pm.parent(master_grp, asset_node, r=1, add=1)

        print('%s:%s:' % (asset_name, asset_file))
