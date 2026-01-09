# coding=utf-8
import sys,os
import maya.api.OpenMaya as om
import maya.cmds as mc
import maya.mel as mel

def optimize_viewport(*args, **kwargs):
    if not load_dx11_plugin():
        return
    # Performance
    mc.setAttr("hardwareRenderingGlobals.maxHardwareLights", 8)
    mc.setAttr("hardwareRenderingGlobals.transparencyAlgorithm", 1)
    mc.setAttr("hardwareRenderingGlobals.transparentShadow", 1)
    mc.setAttr("hardwareRenderingGlobals.defaultLightIntensity",3.1415926)

    mc.setAttr("hardwareRenderingGlobals.enableTextureMaxRes", 1)
    mc.setAttr("hardwareRenderingGlobals.textureMaxResMode", 1)
    mc.setAttr("hardwareRenderingGlobals.textureMaxResolution", 512)
    mel.eval("source AEhardwareRenderingGlobalsTemplate;")
    mel.eval("AEReloadAllTextures;")

    mc.setAttr("hardwareRenderingGlobals.colorBakeResolution", 32)
    mc.setAttr("hardwareRenderingGlobals.bumpBakeResolution", 32)

    # Ambient Occlusion
    mc.setAttr("hardwareRenderingGlobals.ssaoEnable", 1)
    mc.setAttr("hardwareRenderingGlobals.ssaoSamples", 16)

    # Motion Blur
    mc.setAttr("hardwareRenderingGlobals.motionBlurEnable", 0)
    mc.setAttr("hardwareRenderingGlobals.motionBlurSampleCount", 4)

    # Anti Aliasing
    mc.setAttr("hardwareRenderingGlobals.lineAAEnable", 1)
    mc.setAttr("hardwareRenderingGlobals.multiSampleEnable", 1)

    # May result in banding but has a big impact on speed
    mc.setAttr("hardwareRenderingGlobals.floatingPointRTEnable", 0)

    # Animation caching
    mc.setAttr("hardwareRenderingGlobals.vertexAnimationCache", 2)

    # Optimise SkinClusters
    for skin_cluster in mc.ls(type='skinCluster', l=True):
        mc.setAttr(skin_cluster + ".deformUserNormals", 0)

    mc.confirmDialog(title="Viewport Optimisation", message=u"VP2视口Playblast显示设置完成！",icon='information',button=['Yes','No'], defaultButton='Yes', cancelButton='No',)

def load_dx11_plugin():
    import platform
    try:
        system = platform.system()
        project = os.environ['project_name'] if 'project_name' in list(os.environ.keys()) else 'unknown'
    except Exception as ex:
        mc.confirmDialog(title=u"os操作系统错误", message=u'无法获取操作系统信息！',icon='critical',button=['Yes','No'], defaultButton='Yes', cancelButton='No',)
        return None
    if not system == "Windows":
        mc.confirmDialog(title=u"os操作系统错误", 
            message=u'当前操作系统“{0}，不支持DirectX11，无法用于“{1}”项目拍屏！'.format(
                'MacOS' if system == "Darwin" else system,os.environ['project_name']),icon='information',button=['Yes','No'], defaultButton='Yes', cancelButton='No',)
    try:
        mc.loadPlugin('dx11Shader.mll')
    except Exception as ex:
        mc.confirmDialog(title=u"Maya错误", message=u'无法挂载dx11Shader插件，请检查Maya安装！',icon='critical',button=['Yes','No'], defaultButton='Yes', cancelButton='No',)
        return None
    return True


def reset_viewport(*args, **kwargs):
    if not load_dx11_plugin():
        return
    # Reset performance settings to original values
    mc.setAttr("hardwareRenderingGlobals.maxHardwareLights", 1)
    mc.setAttr("hardwareRenderingGlobals.transparencyAlgorithm", 1)

    mc.setAttr("hardwareRenderingGlobals.enableTextureMaxRes", 1)
    mc.setAttr("hardwareRenderingGlobals.textureMaxResMode", 0)
    mc.setAttr("hardwareRenderingGlobals.textureMaxResolution", 2048)
    mel.eval("source AEhardwareRenderingGlobalsTemplate;")
    mel.eval("AEReloadAllTextures;")

    mc.setAttr("hardwareRenderingGlobals.colorBakeResolution", 64)
    mc.setAttr("hardwareRenderingGlobals.bumpBakeResolution", 64)

    # Reset Ambient Occlusion
    mc.setAttr("hardwareRenderingGlobals.ssaoEnable", 0)
    mc.setAttr("hardwareRenderingGlobals.ssaoSamples", 16)

    # Reset Motion Blur
    mc.setAttr("hardwareRenderingGlobals.motionBlurEnable", 0)
    mc.setAttr("hardwareRenderingGlobals.motionBlurSampleCount", 8)

    # Reset Anti Aliasing
    mc.setAttr("hardwareRenderingGlobals.lineAAEnable", 0)
    mc.setAttr("hardwareRenderingGlobals.multiSampleEnable", 0)

    # Reset floating point render target
    mc.setAttr("hardwareRenderingGlobals.floatingPointRTEnable", 1)

    # Reset Animation caching
    mc.setAttr("hardwareRenderingGlobals.vertexAnimationCache", 0)

    # Reset SkinClusters
    for skin_cluster in mc.ls(type='skinCluster', l=True):
        mc.setAttr(skin_cluster + ".deformUserNormals", 1)  # Assuming reset to 1 for deformUserNormals

    #mc.confirmDialog(title="Viewport Optimisation", message=u"VP2视口Playblast显示设置完成！",icon='information',button=['Yes','No'], defaultButton='Yes', cancelButton='No',)

