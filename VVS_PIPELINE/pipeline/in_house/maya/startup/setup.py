# -*-coding:utf-8-*-
import os,imp
import sys
import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om
import maya.utils
from utils import strutils

module_path = strutils.format_path(os.path.dirname(os.path.dirname(__file__)))
in_house_path = strutils.format_path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if os.path.exists(module_path):
    sys.path.append(module_path)



def add_icons_path(path=None):
    if not path:
        path = strutils.format_path_join(module_path, 'res', 'icons')
    else:
        path = strutils.format_path(path)
    icons_path = os.environ.get('XBMLANGPATH')

    if os.path.exists(path) and path not in icons_path:
        print('Adding Icons To XBM Paths : %s' % path)
        os.environ['XBMLANGPATH'] += '%s%s' % (os.pathsep, path)
    else:
        print('Icons Path already setup')


def add_packages_path(path=None):
    major = sys.version_info.major
    minor = sys.version_info.minor
    if os.path.exists(strutils.format_path_join('C:/VVS_PLUGINS/pipeline/in_house','python','py%s%s'%(major,minor))):
        py_path=strutils.format_path_join('C:/VVS_PLUGINS/pipeline/in_house','python','py%s%s'%(major,minor))
    else:
        py_path =strutils.format_path_join(in_house_path,'python','py%s%s'%(major,minor))
    sys.path.append(py_path)

    if not path:
        path = strutils.format_path_join(module_path, 'lib')
    else:
        path = strutils.format_path(path)
    sys.path.append(in_house_path)
    # load maya packages
    lib_path = strutils.format_path_join(path, '%s\site-packages' % cmds.about(v=True))
    if not os.path.exists(lib_path):
        print('cg:lib  Path  not found...')
        return

    if lib_path not in sys.path:
        sys.path.append(lib_path)
        print('cg:Packages Path already setup...')

    libs_path = strutils.format_path_join(in_house_path, 'libs')
    print(libs_path)
    sys.path.append(libs_path)

    # cgteamwork api
    # cg_api_path = strutils.format_path_join(libs_path, 'cg_api')
    # sys.path.append(cg_api_path)

    # vendor
    vendor_path = strutils.format_path_join(in_house_path, 'vendor')
    sys.path.append(vendor_path)
    #stage
    stage_path=strutils.format_path_join(in_house_path, 'stage','UI')
    sys.path.append(stage_path)

    if mel.eval('exists "SubmitJobToDeadline"') == 0:
        submission_dir = 'L:/VVS_PIPELINE/vvs-dcc-plugins/maya/default/submitters/Maya/Main'
        submission_file = '{}/SubmitMayaToDeadline.mel'.format(submission_dir)
        mel.eval('source "{}";'.format(submission_file))


def add_plugins_path(path=None):
    #_onMayaDropped() # studio library
    if not path:
        path = strutils.format_path_join(module_path, 'plug-ins_br')
    else:
        path = strutils.format_path(path)
    plugins = []

    plugin_path = strutils.format_path_join(path, '%s' % cmds.about(v=True))
    if not os.path.exists(plugin_path):
        return

    for plugin in os.listdir(plugin_path):
        if plugin.endswith('.mll') or plugin.endswith('.py'):
            plugins.append(strutils.format_path_join(plugin_path, plugin))

    for plugin in plugins:
        if not cmds.pluginInfo(plugin, query=True, loaded=True):
            # 20250829 if loading plugin failed,copy to local
            try:
                cmds.loadPlugin(plugin)
                print('%s Path already setup...' % os.path.basename(plugin))
            except RuntimeError as err:
                print(err)
                try:
                    import shutil
                    if os.path.splitext(plugin)[1]=='.mll':
                        plugin_dir = '{0}/Autodesk/Maya2025/bin/plug-ins/'.format(os.environ['Programfiles']).replace('\\','/')
                        plugin_mll = os.path.join(plugin_dir,os.path.basename(plugin))
                        os.makedirs(plugin_dir) if not os.path.exists(plugin_dir) else None
                        if not os.path.isfile(plugin_mll):
                            shutil.copy2(plugin,plugin_mll)
                            #cmds.loadPlugin(os.path.join(plugin_dir,os.path.basename(plugin)))
                except PermissionError as err:
                    print(err) 


def Submit_Job_Deadline():
    mel.eval('SubmitJobToDeadline')


def view_transform():
    cmds.colorManagementPrefs(e=True, cmEnabled=True)
    cmds.colorManagementPrefs(e=True, viewTransformName=os.getenv('view_transform'))




def legacy_color(color):
    try:
        mel.eval("changeColorMgtPrefsConfigFilePath(\"%s\")" % color)
    except Exception as e:
        om.MGlobal.displayError(str(e))
        pass
def disable_playback_cache():
    try:
        maya.utils.executeDeferred(cmds.evaluator(name='cache', enable=0))
    except:
        pass

def add_env_config():
    if os.getenv('color_management'):
        cmds.colorManagementPrefs(e=True, policyFileName="")
        if os.getenv('color_management') == 'default':
            try:
                mel.eval("changeColorMgtPrefsConfigFilePath(\"\")")
            except Exception as e:
                om.MGlobal.displayError(str(e))
                pass
    try:
        if os.getenv('view_transform'):
            print(u'view transform:%s' % os.getenv('view_transform'))
            maya.utils.executeDeferred(view_transform)

        if os.getenv('color_space'):
            print(u'color_space:%s' % os.getenv('color_space'))
            maya.utils.executeDeferred(legacy_color, os.getenv('color_space'))

        if os.getenv('output_transform'):
            print(u'output view transform:%s' % os.getenv('output_view_transform'))
            maya.utils.executeDeferred(cmds.colorManagementPrefs(e=True, outputTransformName=os.getenv('output_transform'), outputTarget='playblast'))

    except Exception as e:
        print(e)
        pass


def auto_plugin():
    for plugin_name in ['mtoa', 'AbcExport', 'AbcImport']:
        if not cmds.pluginInfo(plugin_name, query=True, loaded=True):
            try:
                cmds.loadPlugin(plugin_name)
            except Exception as e:
                print(e)
    try:
        mel.eval('optionVar -cat "Cache.GPU Cache" -iv "gpuCacheAllAuto" 0 -iv "gpuCacheBackgroundReading" 0 -iv "gpuCacheBackgroundReadingRefreshAuto" 0;')
    except RuntimeError as err:
        print(err)

def init_arnold():
    from mtoa.core import createOptions
    createOptions()
    cmds.setAttr('defaultArnoldRenderOptions.autotx', 0)
    print('---autotx %s---' % cmds.getAttr('defaultArnoldRenderOptions.autotx'))


def on_scene_new(*args):
    print('---new scene---')
    if os.getenv('AUTOTX') == '0':
        auto_plugin()
        init_arnold()

def on_scene_open(*args):
    print('---open scene---')
    if os.getenv('AUTOTX') == '0':
        cmds.setAttr('defaultArnoldRenderOptions.autotx', 0)
    
def register_callbacks():
    op_events = {}
    op_events[on_scene_new] = om.MSceneMessage.addCallback(om.MSceneMessage.kAfterNew, on_scene_new)
    op_events[on_scene_open] = om.MSceneMessage.addCallback(om.MSceneMessage.kAfterOpen, on_scene_open)
    om.MGlobal.displayInfo("Installed event handler on_scene_new,on_scene_open..")

def fix_gpuCache_bug():
    try:
        mel.eval('gpuCache -query -waitForBackgroundReading `ls -type gpuCache`;')
    except RuntimeError as err:
        print(err)

def menu_setup(parent='MayaWindow'):
    if cmds.menu('vvs', exists=True):
        cmds.deleteUI('VVS')

    if cmds.window(parent, exists=True):
        if not cmds.window(parent, q=True, menuBar=True):
            raise Exception('Menu has no menuBarlayout %s' % parent)
        else:
            vvs_menu = cmds.menu('vvs', l='VVS-%s' % os.environ['project_name'], p=parent, tearOff=True,
                                 allowOptionBoxes=True)
            print('New VVS Menu added to current window : %s' % parent)
    elif cmds.menuBarLayout(parent, exists=True):
        vvs_menu = cmds.menu('vvs', l='VVS', p=parent, tearOff=True, allowOptionBoxes=True)
        print('VVS Menu added to current windows menuBar : %s' % parent)
    else:
        raise Exception('VVS  Menu is invalid %s' % parent)
    
    #20250603 add tools yangyongtao 
    sl_menu = cmds.menuItem('mayatoolsItem', l='Maya Tools', sm=True, p=vvs_menu, tearOff=True, i='toolbox-64.png')
    #20250818 check maya scene
    cmds.menuItem(l='Check Maya Reference Tool', p=sl_menu, tearOff=True, i='settings_94px.png',
                  c='from CheckMayaRef import CheckMayaRef as cmr;dialog=cmr.mainWin(cmr.uiPath,cmr.icoPath);dialog.show()') 
    cmds.menuItem(l='Clear Somethings Tool', p=sl_menu, tearOff=True, i='Dozer.ico',
                  c='from ClearSomeThings import ClearSomeThings as cst;dialog=cst.mainWin(cst.uiPath,cst.icoPath);dialog.show()')  
    #20250620 fork playblast
    cmds.menuItem(l='BR PlayBlast Tool', p=sl_menu, tearOff=True,i='action_64.png',
                  c='import ani_BR.play_blast.play_blast as pl;pl.PlayBlastWidget.display()')
    # 20250915 maya 2025/2026 gpuCache read bug
    cmds.menuItem(l='Fix GpuCache Bug', p=sl_menu, tearOff=True,i='vcard_48px.png',
                  c=lambda _: fix_gpuCache_bug)
    #20250711 3D StoryBoard Replace
    cmds.menuItem(l='3D StoryBoard Replace', p=sl_menu, tearOff=True,i='storyboard_61px.png',
                  c='from StoryBoardReplace import StoryBoardReplace as sbr;dialog=sbr.mainWin(sbr.uiPath,sbr.icoPath);dialog.show()')
    #20250722 add animation tools yangyongtao
    ani_menu = cmds.menuItem('animationtoolsItem', l='Animation Tools', sm=True, p=sl_menu, tearOff=True, i='Supervisor_128px.png')
    cmds.menuItem(l='Shape Animation Tool 2.0', p=ani_menu, tearOff=True, i='model_48px.png',
                  c='from ShapeAnimationTool import sat;imp.reload(sat)')
    cmds.menuItem(l='Anchor Transform', p=ani_menu, tearOff=True, i='AT_icon.png',
                  c='import anchorTransform.ui;anchorTransform.ui.show()')
    cmds.menuItem(l='KeyFrame & Curve Edit Tools', p=ani_menu, tearOff=True, i='movie_48px.png',
                  c='from AnimationTools import KeyFrame;dialog=KeyFrame.mainWin(KeyFrame.uiPath,KeyFrame.icoPath);dialog.show()')
    cmds.menuItem(l='Vectorify Tools <Flow Path>', p=ani_menu, tearOff=True, i='vectorify_icon.png',
                  c='from Vectorify import Vectorify_Drag_and_Drop_installer;from Vectorify import vectorify_script as ves')
    html='L:/VVS_PIPELINE/vvs-dcc-plugins/standalone/mayaDev/Vectorify/VECTORIFY_Guide.mp4'
    cmds.menuItem(l='Vectorify Tools <User Guide>', p=ani_menu, tearOff=True, i='Help.png',
                  c='os.system("@{0}");'.format(html))
    #20250704 add model tools yangyongtao
    mod_menu = cmds.menuItem('modeltoolsItem', l='Model Tools', sm=True, p=sl_menu, tearOff=True, i='object_48px.png')
    cmds.menuItem(l='Check Mesh Topology', p=mod_menu, tearOff=True, i='checkin_64px.png',
                  c='from modelChecker import modelChecker_UI;modelChecker_UI.UI.show_UI();')
    cmds.menuItem(l='Difference Meshes', p=mod_menu, tearOff=True, i='search_64px.png',
                  c='from DifModelJson import difModelJson as dmj;dialog=dmj.mainWin(dmj.uiPath,dmj.icoPath);dialog.show()')
    cmds.menuItem(l='Rename UV to map1', p=mod_menu, tearOff=True, i='uv_64px.png',
                  c='from renameUVmap import renameUV;renameUV.check_selection_type()')
    shd_menu = cmds.menuItem('shadertoolsItem', l='Shader Tools', sm=True, p=sl_menu, tearOff=True, i='checker_64.png')
    cmds.menuItem(l='Rename Shaders By Mesh', p=shd_menu, tearOff=True, i='rename_icon.png',
                  c='import RenameShaderByMesh;RenameShaderByMesh.rename_shaders()')
    cmds.menuItem(l='File Texture Manager', p=shd_menu, tearOff=True, i='ftm_icon.png',
                  c='import maya.mel as mel;mel.eval("FileTextureManager;")')
    cmds.menuItem(l='Merge Shader To Meshes', p=shd_menu, tearOff=True, i='compound_53px.png',
                  c='from ShaderTools import mergeShader;mergeShader.import_shader_for_selected()')
    #202501020 add cfx tools yangyongtao
    cfx_menu = cmds.menuItem('cfxtoolsItem', l='CFX Tools', sm=True, p=sl_menu, tearOff=True, i='bb.png')
    cmds.menuItem(l='XGen Groomer Tools', p=cfx_menu, tearOff=True, i='xgtGuideColor_user.png',
                  c='sys.path.append(r"L:/VVS_PIPELINE/vvs-dcc-plugins/standalone/mayaDev");import xgtc;import xgToolsUI_user_sub;xgToolsUI_user_sub.XgtRun()')
    cmds.menuItem(l='Animation Rig Merge Groom', p=cfx_menu, tearOff=True, i='hair_red_64px.png',
                  c='from AniRigMergeGroom import AniRigMergeGroom as armg;dialog=armg.mainWin(armg.uiPath,armg.icoPath);dialog.show()')
    #20250715 fix Universal Material Builder
    cmds.menuItem(l='Universal Material Builder', p=shd_menu, tearOff=True, i='umb_logo.png',
                  c='import sys;sys.path.append("L:/VVS_PIPELINE/vvs-dcc-plugins/standalone/mayaDev/UniversalMaterialBuilder");import umb_main as umb;umb.openUI()')
    #20250708 add light tools yangyongtao
    lgt_menu = cmds.menuItem('lighttoolsItem', l='Light Tools', sm=True, p=sl_menu, tearOff=True, i='lamp_48px.png')
    cmds.menuItem(l='Arnold Default AOVs', p=lgt_menu, tearOff=True, i='aov_48px.png',
                  c='import ArnoldAOVs;ArnoldAOVs.create_arnold_aov_nodes()')
    cmds.menuItem(l='Lighting Startup Operation', p=lgt_menu, tearOff=True, i='luxo_150px.png',
                  c='from LightStartup import LightStartup as lso;dialog=lso.mainWin(lso.uiPath,lso.icoPath);dialog.show()')
    cmds.menuItem(l='Render Layer Mark', p=lgt_menu, tearOff=True, i='layer_48px.png',
                  c='from RenderLayerMark import RenderLayerMark as rlm;dialog=rlm.mainWin(rlm.uiPath,rlm.icoPath);dialog.show()')
    pub_menu = cmds.menuItem('publishtoolsItem', l='Publish Tools', sm=True, p=sl_menu, tearOff=True, i='publish_icon.png')
    #20250910 checkMesh yangyongtao
    cmds.menuItem(l='Public Model As Update', p=pub_menu, tearOff=True, i='face_edge.png',
                  c='from modelChecker import checkMesh as cm;dialog=cm.mainWin(cm.uiPath,cm.icoPath);dialog.show()')
    cmds.menuItem(l='Shader Export To Json', p=pub_menu, tearOff=True, i='json_icon.png',
                  c='from ExportMaterials import *;emmat.runas_default_args()')
    cmds.menuItem(l='Public Shader As Update', p=pub_menu, tearOff=True, i='shader_32px.png',
                  c='from ShaderTools import shaderPublish;dialog=shaderPublish.mainWin(shaderPublish.uiPath,shaderPublish.icoPath);dialog.show()')
    cmds.menuItem(l='Public Groom As Update', p=pub_menu, tearOff=True, i='furry_60.png',
                  c='from XgenTools import xgenPublish;dialog=xgenPublish.mainWin(xgenPublish.uiPath,xgenPublish.icoPath);dialog.show()')
    cmds.menuItem(l='Public Layout As Update', p=pub_menu, tearOff=True, i='comic_64px.png',
                  c='from LayoutTools import layoutPublish;dialog=layoutPublish.mainWin(layoutPublish.uiPath,layoutPublish.icoPath);dialog.show()')
    cmds.menuItem(l='Public Animation As Update', p=pub_menu, tearOff=True, i='slate_64px.png',
                  c='from AnimationTools import animationPublish;dialog=animationPublish.mainWin(animationPublish.uiPath,animationPublish.icoPath);dialog.show()')
    #20250626 add AssetTransKinds tools
    cmds.menuItem(l='Public Elements Of Sets', p=pub_menu, tearOff=True, i='build_64px.png',
                  c='from AssetTransKinds import setsElementsPublish;dialog=setsElementsPublish.mainWin(setsElementsPublish.uiPath,setsElementsPublish.icoPath);dialog.show()')
    imp_menu = cmds.menuItem('importtoolsItem', l='Import Tools', sm=True, p=sl_menu, tearOff=True, i='import_icon.png')
    cmds.menuItem(l='Import Elements To Animation', p=imp_menu, tearOff=True, i='animation64px.png',
                  c='from AnimationTools import animationImport;dialog=animationImport.mainWin(animationImport.uiPath,animationImport.icoPath);dialog.show()')
    #20250721 add AssetRefImp & AssetReplace tools
    cmds.menuItem(l='Import Rig With Reference', p=imp_menu, tearOff=True, i='storage_55px.png',
                  c='from AssetsRefImp import AssetsRefImp;dialog=AssetsRefImp.mainWin(AssetsRefImp.uiPath,AssetsRefImp.icoPath);dialog.show()')
    cmds.menuItem(l='Switch Rig In AssetLibs', p=imp_menu, tearOff=True, i='reload_50px.png',
                  c='from AssetsRefImp import AssetsReplace;dialog=AssetsReplace.mainWin(AssetsReplace.uiPath,AssetsReplace.icoPath);dialog.show()')
    #20250701 add AssetTransKinds tools
    cmds.menuItem(l='Switch Parts Of Elements In Sets', p=imp_menu, tearOff=True, i='kindtools.png',
                  c='from AssetTransKinds import assetTransKind;dialog=assetTransKind.mainWin(assetTransKind.uiPath,assetTransKind.icoPath);dialog.show()')
    #20250626 add AssetTransKinds tools
    cmds.menuItem(l='Import Elements Rebuild Sets', p=imp_menu, tearOff=True, i='map_64px.png',
                  c='from AssetTransKinds import setsElementsImport;dialog=setsElementsImport.mainWin(setsElementsImport.uiPath,setsElementsImport.icoPath);dialog.show()')
    #20251113 export ass tools.
    ass_menu = cmds.menuItem('asstoolsItem', l='ASS Tools', sm=True, p=sl_menu, tearOff=True, i='ExportStandinShelf_150.png')
    cmds.menuItem(l='Export ASS Tools', p=ass_menu, tearOff=True, i='supplier_94px.png',
                  c='from ArnoldAss import ArnoldAss as aa;dialog=aa.mainWin(aa.uiPath,aa.icoPath);dialog.show()')
    cmds.menuItem(l='ASS Kit Tools', p=ass_menu, tearOff=True, i='workflow-94px.png',
                  c='from ArnoldAss import AssKit as ak;dialog=ak.mainWin(ak.uiPath,ak.icoPath);dialog.show()')
    #20250627 add Baking tools. code from DD Wang
    bake_menu = cmds.menuItem('baketoolsItem', l='Bake Tools', sm=True, p=sl_menu, tearOff=True, i='baking_64px.png')
    cmds.menuItem(l='Bake Camera From CamRig', p=bake_menu, tearOff=True, i='camera_64px.png',
                  c='import MayaBakeCamera;MayaBakeCamera.ui_startup()')
    cmds.menuItem(l='VVS Clone Camera', p=bake_menu, tearOff=True, i='vcam_94px.png',
                  c='from VVSCamera import VVSCamera as vc;dialog=vc.mainWin(vc.uiPath,vc.icoPath);dialog.show()')
    cmds.menuItem(l='Extend Two Alembic Files', p=bake_menu, tearOff=True, i='objects_64px.png',
                  c='from AlembicKeyBlender import AlembicKeyBlender as ab;ab.mainUI(ab.uiPath,ab.icoPath)')
    cmds.menuItem(l='Bake Tensify Maps', p=bake_menu, tearOff=True, i='Bucket.ico',
                  c='import BakeTensifyMaps as btm;btm.bake_attrMaps_as_sequence() if btm.load_tensify() else None')
    #20250624 add dreamwallpicker wangruilong
    rig_menu = cmds.menuItem('rigtoolsItem', l='Rig Tools', sm=True, p=sl_menu, tearOff=True, i='skeleton_64px.png')
    cmds.menuItem(l='Picker Loader', p=rig_menu, tearOff=True, i='dreamwallpicker.png',
                  c='import load_picker;load_picker.create_picker_loader()')
    
    #20250528 add studiolib yangyongtao 
    sl_menu = cmds.menuItem('studiolibItem', l='Studio Library', sm=True, p=vvs_menu, tearOff=True, i='studioLib_logo.png')
    cmds.menuItem(l='Studio Library...', p=sl_menu, tearOff=True,
                  c='import studiolibrary;studiolibrary.main()')

    sur_menu = cmds.menuItem('surfaceItem', l='Shader : Texture', sm=True, p=vvs_menu, tearOff=True, i='checker_64.png')

    cmds.menuItem(l='Export Shader...', p=sur_menu, tearOff=True,
                  c='import core.srf.export_material as export_material;import importlib;importlib.reload(export_material);export_material.main()')

    cmds.menuItem(l='Import Shader...', p=sur_menu, tearOff=True,
                  c='import core.srf.import_material as import_material;import importlib;importlib.reload(import_material);import_material.main()')

    cmds.menuItem(l='Import aiStandIn Shader...', p=sur_menu, tearOff=True,
                  c='import core.srf.import_aistandin_material as import_aistandin_material;import importlib;importlib.reload(import_aistandin_material);import_aistandin_material.main()')

    cmds.menuItem(l='Set Texture ColorSpace...', p=sur_menu, tearOff=True,
                  c='import core.srf.set_file_color_space as set_file_color_space;import importlib;importlib.reload(set_file_color_space);set_file_color_space.main()')

    cmds.menuItem(l='Scale UV...', p=sur_menu, tearOff=True,
                  c='import core.srf.uv_scale as uv_scale;import importlib;importlib.reload(uv_scale);uv_scale.main()')

    ani_menu = cmds.menuItem('aniItem', l='Ani', sm=True, p=vvs_menu, tearOff=True, i='videoAdd_64.png')

    cmds.menuItem(l='PlayBalst', p=ani_menu, tearOff=True,
                  c='import core.ani.play_blast.play_blast as pl;pl.PlayBlastWidget.display()')

    cmds.menuItem(l='Import Nuke Retime', p=ani_menu, tearOff=True,
                  c='import core.ani.import_nuke_retime.import_app as retime_import;retime_import.main()')

    mocap_file = strutils.format_path_join(module_path, 'scripts', 'core', 'ani', 'mocap', 'mocap.mel')
    cmds.menuItem(l='Import Mocap FBX', p=ani_menu, tearOff=True,
                  c="import maya.mel as mel;mel.eval('source \"%s\"')" % mocap_file)

    misc_menu = cmds.menuItem('miscItem', l='Misc', sm=True, p=vvs_menu, tearOff=True, i='wrench_64.png')

    cmds.menuItem(l='Outliner Sort', p=misc_menu, tearOff=True,
                  c='import core.misc.outliner_sort as out_sort;out_sort.main()')

    cmds.menuItem(l='Add Exr TimeCode', p=misc_menu, tearOff=True,
                  c='import core.misc.time_code.exr_time_code as etc;import importlib;importlib.reload(etc);etc.main()')
                  
    cmds.menuItem(l='ArchiveScene', p=misc_menu, tearOff=True,
                  c='import core.batch.batch_archive.zip_scene as zips;import importlib;importlib.reload(zips);zips.zipScene(True,mode=2)')

    light_menu = cmds.menuItem('lightItem', l='Lgt', sm=True, p=vvs_menu, tearOff=True, i='lightarea_64.png')

    cmds.menuItem(l='Reference Abc Sequence', p=light_menu, tearOff=True,
                  c='import  sys;import importlib;import core.ani.abc_cache as abc_cache;importlib.reload(abc_cache);abc_cache.referenct_abc()')
                  
    look_dev_menu = cmds.menuItem('lookDevXItem', l='LookDevX', sm=True, p=vvs_menu, tearOff=True, i='lightarea_64.png')
    cmds.menuItem(l='Rename', p=look_dev_menu, tearOff=True,
                  c='import  sys;import importlib;import core.lookdevx.rename.rename_app as rename_app ;importlib.reload(rename_app);rename_app.main()')

    if sys.version_info.major >=3 and sys.version_info.minor >=9:
        cmds.menuItem(l='Convert Arnold to Mtlx', p=look_dev_menu, tearOff=True,
                  c='import  mtlxLib;mtlxLib.create_mtlx_document()')

    # cmds.menuItem(l='Reference Abc Sequence', p=vvs_menu, tearOff=True,
    # c='import  sys;import importlib;import core.ani.abc_reference as abc_reference;importlib.reload(abc_reference);abc_reference.reference()')

    cmds.menuItem(l='Import  aiStandin Abc Sequence', p=light_menu, tearOff=True,
                  c='import  sys;import importlib;import core.ani.import_aistandin_abc as import_aistandin_abc;importlib.reload(import_aistandin_abc);import_aistandin_abc.import_abc()')

    # cmds.menuItem(l='TEST Import  aiStandin Abc Sequence', p=vvs_menu, tearOff=True,
    # c='import  sys;import importlib;import core.ani.test_import_aistandin as test_import_aistandin;importlib.reload(test_import_aistandin);test_import_aistandin.main()')

    # cmds.menuItem(l='Select Reference Use Sequence', p=vvs_menu, tearOff=True,
    #               c='import  sys;import importlib;import core.ani.abc_reference as abc_reference;importlib.reload(abc_reference);abc_reference.reference_use_sequence()')

    unreal_menu = cmds.menuItem('unrealItem', l='UE', sm=True, p=vvs_menu, tearOff=True, i='unreal_64.png')

    cmds.menuItem(l='Xgen 2 UE ...', p=unreal_menu, tearOff=True,
                  c='import core.xgen.xgen_2_ue as x2u;import importlib;importlib.reload(x2u);x2u.main()')

    cmds.menuItem(l='metahuman_facial', p=unreal_menu, tearOff=True,
                  c='import core.misc.metahuman_facial_transfer.metahuman_facial_transfer as mft;import importlib;importlib.reload(mft);mft.UI()')

    cmds.menuItem(divider=True, parent=vvs_menu)

    cmds.menuItem(l='Manager', p=vvs_menu, tearOff=True,
                  c='from time import time;start = time();from stage.UI import main;win=main.launch();end = time();print("Took %s seconds"%(end - start))')

    cmds.menuItem(l='Publish', p=vvs_menu, tearOff=True,
                  c='from stage.UI import main;from stage.UI import main;win=main.launch(dont_show=True);win.publish_scene()')

    cmds.menuItem(divider=True, parent=vvs_menu)

    cmds.menuItem('deadlineItem', l='Submit Deadline', p=vvs_menu, tearOff=True, i='Submit.png',
                  c=lambda _: Submit_Job_Deadline())
    cmds.menuItem('generateAllUvTilePreviewsItem', l='generateAllUvTilePreviews', p=vvs_menu, tearOff=True, i='refresh_64.png',
                  c='import core.misc.refresh_texture as ref_tex;import importlib;importlib.reload(ref_tex);ref_tex.main()')




def start(parent_menu='MayaWindow'):
    add_plugins_path()
    if cmds.about(batch=True):
        return

    add_icons_path()
    add_packages_path()

    add_env_config()

    menu_setup(parent=parent_menu)

    on_scene_new()
    disable_playback_cache()
    register_callbacks()
