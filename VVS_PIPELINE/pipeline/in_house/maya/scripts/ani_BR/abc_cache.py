import os, sys
import maya.cmds as cmds
from Qt import QtWidgets, QtCore, QtGui
import maya.OpenMayaUI as omui
from Qt import QtCompat
from common import fileseq


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    if sys.version_info.major >= 3:
        return QtCompat.wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    else:
        return QtCompat.wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


def abc_2_maya():
    abc_file, file_type = QtWidgets.QFileDialog.getOpenFileName(maya_main_window(), 'referebce%s Abc [ abc ]',
                                                                os.getcwd(),
                                                                'Abc Files (*.abc)')
    if not abc_file:
        return
    if not abc_file.lower().endswith('.abc'):
        return

    fs = fileseq.findSequenceOnDisk(os.path.normpath(abc_file))

    frame = fs.start()
    zfill=fs.zfill()
    print(frame,zfill)

    ns = os.path.basename(abc_file).split('.')[0]
    cmds.file(abc_file, r=True, ignoreVersion=True, namespace=ns)
    abc_file_dir = os.path.dirname(abc_file).replace('\\', '/')
    py_code = '''python("import maya.cmds as cmds\\ntime = cmds.currentTime(q=True)\\ncurrent_time=str(int(time))\\nfname='abc_file_dir/base_name.%s.abc'%str(current_time).zfill({0})\\ncmds.file(fname, loadReference='base_nameRN')");'''.format(zfill)
    cmds.setAttr('defaultRenderGlobals.preRenderMel',
                 py_code.replace('abc_file_dir', abc_file_dir).replace('base_name', ns), type='string')

    py = '''
import maya.cmds as cmds
def on_time_changed():
    time = cmds.currentTime(q=True)
    current_time = str(int(time))
    f_name = "abc_file_dir/base_name.%s.abc" %str(current_time).zfill({0})
    cmds.file(f_name, loadReference="base_nameRN")
on_time_changed()
'''.format(zfill)
    node_name = cmds.scriptNode(st=7, bs=py.replace("'''", "''").replace('abc_file_dir', abc_file_dir).replace('base_name', ns), n='abc_sequence_%s'%ns, stp='python')

def referenct_abc():
    abc_2_maya()
