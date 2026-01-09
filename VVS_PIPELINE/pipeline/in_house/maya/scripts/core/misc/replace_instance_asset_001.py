import pymel.core as pm
import os
import re

asset_path = 'R:/1023_TLD/ProductionFolder/FromClient/20240521_CSM_TO01/scans/cesiumContainerArea/assets/props/{asset_name}/assembly/{asset_name}_HI_GRP'
asset_file = '{version_path}/maya/{file}'

selects = pm.ls(sl=1)
for sel in selects:
    asset_name = sel.name()[:-1]
    childes = sel.listRelatives(c=1)
    versions = []

    version_path = asset_path.format(asset_name=asset_name)
    print(version_path)
    for d in os.listdir(version_path):
        if re.match(r'v.*?', d, re.I):
            versions.append(d)

    versions.sort()

    maya_file = None
    ma_file_dir = os.path.join(version_path, versions[0], 'maya')
    for f in os.listdir(ma_file_dir):
        print(f)
        if re.findall(r'%s' % asset_name, f, re.I):
            maya_file = os.path.join(ma_file_dir, f)
    print(maya_file)

    ret = pm.importFile(maya_file, returnNewNodes=1)

    master = None
    for r in ret:
        if re.match(r'master$|\|master$', r.name(), re.I):
            master = r
    print(master)
    print(ret)
    print(child)
    for child in childes:
        if re.match(r'.*?_inst$', child.name(), re.I):
            pm.parent(master, child, r=1, add=1)
        else:
            pm.parent(master, child, r=1)



