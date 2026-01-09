import maya.cmds as cmds
from mtoa import core


def add_attribute(code_node, driver_custom_attr):
    next = 0
    if not cmds.objExists('defaultArnoldDriver'):
        core.createOptions()

    if cmds.attributeQuery('customAttributes', node='defaultArnoldDriver', exists=True):
        if cmds.getAttr(driver_custom_attr, multiIndices=True):
            next = cmds.getAttr(driver_custom_attr, multiIndices=True)[-1] + 1
    cmds.connectAttr(code_node + '.outputTimeCode', 'defaultArnoldDriver.customAttributes[%s]' % next, f=True)


def main():
    try:
        driver_custom_attr = "defaultArnoldDriver.customAttributes"
        time_code_node = cmds.ls(type='timeCodeNode')
        time_node = cmds.ls(type='time')[0]

        if time_code_node:
            cmds.delete(time_code_node)

        code_node = cmds.createNode('timeCodeNode')
        cmds.setAttr(code_node + '.name', 'time_code', type='string')
        cmds.connectAttr(time_node + '.outTime', code_node + '.inputTime', f=True)
        add_attribute(code_node, driver_custom_attr)
    except  Exception as e:
        print(e)
        cmds.confirmDialog(
            title=u'错误',
            message='创建 EXR 时间码错误！',
            button=['OK'],
            defaultButton='OK',
            icon='critical'
        )

    cmds.confirmDialog(
        title=u'消息',
        message='创建TimeCode完成！',
        button=['OK'],
        defaultButton='OK',
        icon='information'
    )
