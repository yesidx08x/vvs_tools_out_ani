# -*-coding:utf-8-*-
import os,sys
import maya.cmds as cmds
import maya.mel as mel
from startup import setup as setup
#20250603 add tools yangyongtao 
sys.path.append(r'L:\\VVS_PIPELINE\\vvs-dcc-plugins\\standalone\\mayaDev')
#20250528 add studiolib yangyongtao 
def _onMayaDropped():
    """Dragging and dropping this file into the scene executes the file."""
    sl_path = 'L:/VVS_PIPELINE/vvs-dcc-plugins/standalone/studiolibrary-main'

    srcPath = os.path.join(sl_path, 'src')
    iconPath = os.path.join(srcPath, 'studiolibrary', 'resource', 'icons', 'icon.png')

    srcPath = os.path.normpath(srcPath)
    iconPath = os.path.normpath(iconPath)

    if not os.path.exists(iconPath):
        raise IOError('Cannot find ' + iconPath)

    for path in sys.path:
        if os.path.exists(path + '/studiolibrary/__init__.py'):
            cmds.warning('Studio Library is already installed at ' + path)
    if not os.path.exists(srcPath):
        raise IOError(r'The source path "{path}" does not exist!')
    
    if r'{path}' not in sys.path:
        sys.path.insert(0, srcPath)

#    command = '''
# -----------------------------------
# Studio Library
# www.studiolibrary.com
# -----------------------------------

#import os
#import sys
    
#if not os.path.exists(r'{path}'):
#    raise IOError(r'The source path "{path}" does not exist!')
    
#if r'{path}' not in sys.path:
#    sys.path.insert(0, r'{path}')
    
#import studiolibrary
#studiolibrary.main()
#'''.format(path=srcPath)

#    shelf = mel.eval('$gShelfTopLevel=$gShelfTopLevel')
#    parent = cmds.tabLayout(shelf, query=True, selectTab=True)
#    cmds.shelfButton(
#        command=command,
#        annotation='Studio Library',
#        sourceType='Python',
#        image=iconPath,
#        image1=iconPath,
#        parent=parent
#    )

    # print("\n// Studio Library has been added to current shelf.")

def start(parent_menu='MayaWindow'):
    cmds.evalDeferred("import startup;startup._onMayaDropped();startup.setup.start(parent_menu='%s')" % parent_menu)
