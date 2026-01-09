import maya.mel as mel
import maya.cmds as cmds

def main():
    cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", 1)
    cmds.setAttr("hardwareRenderingGlobals.multiSampleCount", 2)
    mel.eval('generateAllUvTilePreviews;')
    # cmds.refresh(force=True)