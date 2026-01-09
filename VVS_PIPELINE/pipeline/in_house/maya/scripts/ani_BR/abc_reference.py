
import os, sys
import re
import maya.cmds as cmds
from Qt import QtWidgets, QtCore, QtGui
import maya.OpenMayaUI as omui
import maya.api.OpenMaya as om2
from Qt import QtCompat

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    if sys.version_info.major >= 3:
        return QtCompat.wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    else:
        return QtCompat.wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

def reference():
    abc_file, file_type = QtWidgets.QFileDialog.getOpenFileName(maya_main_window(), 'referebce Abc [ abc ]',
                                                                os.getcwd(),
                                                                'Abc Files (*.abc)')
    if not abc_file:
        return
    if not abc_file.lower().endswith('.abc'):
        return

    abc_node = cmds.createNode('AlembicSequenceNode')
    cmds.expression(s='%s.frame=frame' % abc_node)
    cmds.setAttr('%s.filePath' % abc_node, abc_file, type='string')

    nodes = cmds.file(abc_file, reference=True, type="Alembic", ignoreVersion=True, returnNewNodes=True,options="v=0;")
    reference_node = cmds.ls(nodes, type='reference', shortNames=True)
    cmds.lockNode(reference_node, lock=False)
    cmds.addAttr(reference_node, longName='nodeName', dataType='string')
    cmds.addAttr(reference_node, ln="frame", at='long', dv=0)
    cmds.setAttr('%s.frame' % reference_node[0], e=1, keyable=True)
    cmds.setAttr('%s.nodeName' % reference_node[0], reference_node[0], type='string')
    cmds.connectAttr('%s.nodeName'%reference_node[0],'%s.referenceName'%abc_node,f=True)
    cmds.connectAttr('%s.output' % abc_node, '%s.frame' % reference_node[0], f=True)
    cmds.lockNode(reference_node, lock=True)


def reference_use_sequence():
    reference_nodes = cmds.ls(sl=1)
    for reference_node in reference_nodes:
        if not cmds.nodeType(reference_node) == 'reference':
            om2.MGlobal.displayError('%s not is reference...' % reference_node)
            continue
        temp_file_path = cmds.referenceQuery(reference_node, filename=True, withoutCopyNumber=True)
        file_path = re.sub(r'\{\d+\}', '', temp_file_path)

        if not file_path:
            return
        abc_node = cmds.createNode('AlembicSequenceNode')
        cmds.expression(s='%s.frame=frame' % abc_node)
        cmds.setAttr('%s.filePath' % abc_node, file_path, type='string')

        cmds.lockNode(reference_node, lock=False)
        if not cmds.attributeQuery('nodeName', node=reference_node, exists=True):
            cmds.addAttr(reference_node, longName='nodeName', dataType='string')
        if not cmds.attributeQuery('frame', node=reference_node, exists=True):
            cmds.addAttr(reference_node, ln="frame", at='long', dv=0)
        cmds.setAttr('%s.frame' % reference_node, e=1, keyable=True)
        cmds.setAttr('%s.nodeName' % reference_node, reference_node, type='string')
        cmds.connectAttr('%s.nodeName' % reference_node, '%s.referenceName' % abc_node, f=True)
        cmds.connectAttr('%s.output' % abc_node, '%s.frame' % reference_node, f=True)
        cmds.lockNode(reference_node, lock=True)
