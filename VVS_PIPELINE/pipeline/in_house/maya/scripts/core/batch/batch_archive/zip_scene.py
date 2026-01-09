import maya

maya.utils.loadStringResourcesForModule(__name__)
import os
import re
import glob
import zlib
import zipfile
import maya.cmds as cmds
import xgenm as xgen
import xgenm.XgExternalAPI as xge
import pymel.core as pm

from common import fileseq

print('archive files')


def format_path(path):
    return os.path.normpath(path).replace('\\', '/').replace('\t', '/t').replace('\n', '/n').replace('\a', '/a')


def format_path_join(path, *paths):
    return format_path(os.path.join(path, *paths))


def replace_path(pack_path, old_file):
    drive, file_path = os.path.splitdrive(old_file)
    new_file = pack_path + file_path
    return format_path(new_file)


def seq_to_glob(path):
    if path is None:
        return path

    patterns = {
        "<udim>": "<udim>",
        "<tile>": "<tile>",
        "<uvtile>": "<uvtile>",
        "#": "#",
        "u<u>_v<v>": "<u>|<v>",
        "<frame0": "<frame0\d+>",
        "<f>": "<f>"
    }

    lower = path.lower()
    has_pattern = False
    for pattern, regex_pattern in patterns.items():
        if pattern in lower:
            path = re.sub(regex_pattern, "*", path, flags=re.IGNORECASE)
            has_pattern = True

    if has_pattern:
        return path

    base = os.path.basename(path)
    matches = list(re.finditer(r'\d+', base))
    if matches:
        match = matches[-1]
        try:
            new_base = '{0}*{1}'.format(base[:match.start()], base[match.end():])
        except Exception as e:
            print(match.groups(), path, e)
            pass
        head = os.path.dirname(path)
        return os.path.join(head, new_base)
    else:
        return path


class CollectReference(object):

    def search(self):
        result = []
        all_refs = pm.listReferences()

        for ref in all_refs:
            fs = fileseq.findSequenceOnDisk(os.path.normpath(ref.path))

            if len(fs) > 1:
                for f in fs:
                    result.append(f.replace('\\', '/'))
            else:
                result.append(str(ref.path))

        return result
class CollectMetahumanDna(object):
    def search(self):
        result = []
        all_dnas = pm.ls(type='embeddedNodeRL4')
        for dna in all_dnas:
            dna_file=dna.attr('dnaFilePath').get()
            if os.path.exists(dna_file):
                result.append(dna_file)
        return result

class CollectFileDependencies(object):
    register_type_dict = {
        'AlembicNode.abc_File': 'Alembic',
        'gpuCache.cacheFileName': 'gpuCache',
    }

    def __init__(self):

        self.register_type()

    def register_type(self):
        for node, lable in self.register_type_dict.items():
            cmds.filePathEditor(registerType=node, typeLabel=lable)
        cmds.filePathEditor(refresh=True)

    def search(self):

        result = []
        print('filePathEditor:',cmds.filePathEditor(query=True, listDirectories="", unresolved=True))
        if not cmds.filePathEditor(query=True, listDirectories="", unresolved=True):
            return []
        for dir in cmds.filePathEditor(query=True, listDirectories="", unresolved=True):
            files = cmds.filePathEditor(query=True, listFiles=dir, withAttribute=True)
            for (file, node) in zip(*[iter(files)] * 2):
                file = format_path_join(dir, file)
                attr_type = cmds.filePathEditor(node, query=True, attributeType=True)
                image_path = os.path.dirname(file)
                image_name = os.path.basename(file)
                match = re.search(r'(\$[A-Za-z_][A-Za-z0-9_]*)', file)
                if match:
                    var_name = match.group(1)
                    env_name = match.group(1).lstrip('$')
                    file = os.getenv(env_name) + file.split(var_name)[-1]

                glob_pattern = seq_to_glob(file)

                if glob_pattern:
                    glob_files = glob.glob(glob_pattern)
                    if glob_files:
                        if isinstance(glob_files, list):
                            result += glob_files

                        if isinstance(glob_files, str):
                            result.append(glob_files)
                else:
                    result.append(format_path(file))

        return result


class CollectXgen(object):
    def get_aux_cache(self, palette, description):
        object = 'RendermanRenderer'
        attr = 'custom__arnold_auxRenderPatch'
        cache = xgen.getAttr(attr, palette, description, object)
        return cache

    def search(self):
        result = []
        palettes = cmds.ls(type='xgmPalette')
        for palette in palettes:
            descriptions = xgen.descriptions(palette)
            for description in descriptions:
                cache = self.get_aux_cache(palette, description)
                if cache:
                    result.append(cache)

        return result

class CollectAssProxy(object):

    def search(self):
        try:
            import arnold as ar
        except Exception as e:
            print(e)
            return []

        result = []
        nodes = cmds.ls(type="aiStandIn")

        if not nodes: return []

        paths = list(set([cmds.getAttr(node + ".dso") for node in nodes]))
        if not paths: return []

        for ass in paths:
            ar.AiBegin()
            ar.AiMsgSetConsoleFlags(ar.AI_LOG_ALL)
            ar.AiASSLoad(ass, ar.AI_NODE_ALL)
            iterator = ar.AiUniverseGetNodeIterator(ar.AI_NODE_ALL)

            while not ar.AiNodeIteratorFinished(iterator):
                node = ar.AiNodeIteratorGetNext(iterator)
                if ar.AiNodeIs(node, "MayaFile") or ar.AiNodeIs(node, "image"):
                    path = ar.AiNodeGetStr(node, "filename")
                    fs_file = fileseq.findSequenceOnDisk(os.path.normpath(path))
                    if len(fs_file) > 1:
                        for f in fs_file:
                            result.append(f.replace('\\', '/'))
                    else:
                        result.append(format_path(path))

            ar.AiNodeIteratorDestroy(iterator)
            ar.AiEnd()
            fs_ass = fileseq.findSequenceOnDisk(os.path.normpath(ass))
            if len(fs_ass) > 1:
                for f in fs_ass:
                    result.append(f.replace('\\', '/'))
            else:
                result.append(format_path(ass))

        return list(set(result))


def pyError(errorString):
    """ print an error message """
    import maya.mel as mel
    try:
        mel.eval('error "%s"' % errorString)
    except:
        pass


def pyResult(resultString):
    """ print a result message """
    import maya.mel as mel
    msg = maya.stringTable['y_maya_app_general_zipScene.kResult'] % resultString
    mel.eval('print "%s"' % msg)


# checks if filePath is a subdirectory of MAYA_LOCATION
def __isInInstallPath(filePath):
    import maya.mel as mel
    import re
    from os import path as os_path
    mayaLocation = os_path.realpath(mel.eval('getenv MAYA_LOCATION')).replace('\\', '/')
    fileLocation = os_path.realpath(filePath).replace('\\', '/')

    return re.match('{}/*'.format(mayaLocation), fileLocation)


# get a list of all the files associated with the materials in the scene
# that are not on MAYA_LOCATION
def __materialFiles():
    files = []
    materials = cmds.ls(materials=True)
    for material in materials:
        listAttributes = cmds.listAttr(material, usedAsFilename=True)
        if listAttributes:
            for attribute in listAttributes:
                name = '{}.{}'.format(material, attribute)
                attribute = cmds.getAttr(name)
                # if not __isInInstallPath(attribute):
                files.append(attribute)
    return files


# returns a list of the files associated with the scene that are not on MAYA_LOCATION
def __filesInTheScene():
    files = []
    filesInTheScene = cmds.file(query=1, list=1, withoutCopyNumber=1)
    for file in filesInTheScene:
        if not __isInInstallPath(file):
            files.append(file)
    return files

img_extensions = [
        '.jpeg',
        '.jpg',
        '.tiff',
        '.tif',
        '.png',
        '.exr',
        '.hdr',
        '.bmp',
        '.tga',
    ]

def zipScene(archiveUnloadedReferences,output_path='', mode=2):
    fileName = cmds.file(q=True, sceneName=True)

    # If the scene has not been saved
    if (fileName == ""):
        pyError(maya.stringTable['y_maya_app_general_zipScene.kSceneNotSavedError'])
        return

        # If the scene has been created, saved and then erased from the disk
    elif (cmds.file(q=True, exists=True) == 0):
        msg = maya.stringTable['y_maya_app_general_zipScene.kNonexistentFileError'] % fileName
        pyError(msg)
        return

    # If the scene has been modified

    elif (cmds.file(q=True, anyModified=True) == 1):

        if (cmds.about(batch=True)):
            # batch mode, save the scene automatically.
            cmds.warning(maya.stringTable['y_maya_app_general_zipScene.kSavingSceneBeforeArchiving'])
            # cmds.file(force=True, save=True)
        # else:
        #     noStr = maya.stringTable['y_maya_app_general_zipScene.kArchiveSceneNo']
        #     yesStr = maya.stringTable['y_maya_app_general_zipScene.kArchiveSceneYes']
        #     dismissStr = 'dismiss'
        #     result = cmds.confirmDialog(title=maya.stringTable['y_maya_app_general_zipScene.kArchiveSceneTitle'],
        #                                 message=maya.stringTable['y_maya_app_general_zipScene.kArchiveSceneMsg'], \
        #                                 button=[yesStr, noStr], defaultButton=yesStr, cancelButton=noStr,
        #                                 dismissString=dismissStr)
        #     if (result == yesStr):
        #         cmds.file(force=True, save=True)
        #     elif (result == dismissStr):
        #         return
                # get the default character encoding of the system
    from sys import version_info as sys_version_info
    if sys_version_info[0] < 3:
        theLocale = cmds.about(codeset=True)

    files = []
    # Get all files in the scene that are not in the MAYA_LOCATION
    if int(mode) == 1:
        files.extend(__filesInTheScene())
    if int(mode) == 2:
        cfd = CollectFileDependencies()
        files.extend([format_path(f) for f in cfd.search()])
        print('file dependencies count:', len(files))
        print('file dependencies:', files)

    cxc = CollectXgen()
    files.extend([format_path(f) for f in cxc.search()])
    # Get all files associated with the materials in the scene

    # for file in files:
    #     name_noext, ext = os.path.splitext(file)
    #     if ext in img_extensions:
    #         txpath_exp = format_path_join(name_noext + '.tx')
    #         if not os.path.exists(txpath_exp):
    #             txpath_exp = name_noext +'_Utility - sRGB - Texture_ACES - ACEScg'+ext+'.tx'
    #         files.append(txpath_exp)

    files.extend([f for f in __materialFiles() if f])
    print('file dependencies count:', len(files))
    # create a zip file named the same as the scene by appending .zip to the name.
    # this need to be done before set(files) because set won't keep the order of filenames but we rely on that order to get the first one to construct zipFileName.
    mayaFile=cmds.file(query=True, sceneName=True)
    zipFileName = cmds.file(query=True, sceneName=True) + '.zip'
    files.append(mayaFile)


    if output_path:
        zipFileName=output_path +'/'+ os.path.basename(zipFileName)

    print('--------------------', zipFileName)

    zip = zipfile.ZipFile(zipFileName, 'w', zipfile.ZIP_DEFLATED, allowZip64=True)

    # If user choose to archive unloaded reference files, then find all referenced files of the current scene.
    # For any unloaded reference, load them first, get file list that should be archived and then restore its unloaded status.

    # if( archiveUnloadedReferences == True):
    # refNodes = cmds.ls(type='reference')
    # isLoadOldList = []
    # for refNode in refNodes:
    # if(refNode.find('sharedReferenceNode') == -1):
    # try:
    # isLoadOld = cmds.referenceQuery(refNode, isLoaded=True)
    # except Exception as e:
    # print(115,e)
    # continue
    # isLoadOldList.append(isLoadOld)
    # # Load the unloaded reference
    # if(isLoadOld == False):
    # cmds.file(loadReference=refNode, loadReferenceDepth = 'all')
    # # Get all external files related to this reference
    # filesOfThisRef = cmds.file(query=1, list=1, withoutCopyNumber=1)

    # for fileOfThisRef in filesOfThisRef:
    # fs = fileseq.findSequenceOnDisk(os.path.normpath(fileOfThisRef))

    # if len(fs)>1:
    # for f in fs:
    # files.append(f.replace('\\','/'))
    # files.append(fileOfThisRef)
    # # Get all files associated with the materials in the reference

    # files.extend(__materialFiles())
    # # Unload the reference that are unloaded at the beginning
    # if(isLoadOld == False):
    # cmds.file(unloadReference=refNode)
    # # remove the possible duplicated file names

    crr = CollectReference()
    files.extend([format_path(f) for f in crr.search()])
    cma=CollectMetahumanDna()
    files.extend([format_path(f) for f in cma.search()])
    cas = CollectAssProxy()
    files.extend([format_path(f) for f in cas.search()])
    files = set(files)
    files = list(files)

    # add the project workspace.mel file also
    workspacePath = cmds.workspace(q=True, fullName=True) + '/workspace.mel'
    files.append(workspacePath)
    print('file count:',len(files))
    print('files:',files)

    # add each file associated with the scene, including the scene
    # to the .zip file
    exist_txt = open(zipFileName + '.txt', 'w', encoding='utf-8')
    no_exist_txt = open(zipFileName + '_miss.txt', 'w', encoding='utf-8')
    for file in files:
        from os import path as os_path
        if os.path.exists(file):
            exist_txt.write(file+ '\n')
        else:
            no_exist_txt.write(file + '\n')

        if os_path.isfile(file):

            from sys import version_info as sys_version_info
            if sys_version_info[0] >= 3:
                zip.write(file)
            else:
                name = file.encode(theLocale)
                zip.write(name)
        else:
            msg = maya.stringTable['y_maya_app_general_zipScene.kArchiveFileSkipped'] % file
            cmds.warning(msg)
    zip.close()
    exist_txt.close()
    no_exist_txt.close()
    pyResult(zipFileName)
