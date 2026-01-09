import json
import os
from collections import defaultdict
from maya import cmds
import maya.api.OpenMaya as om
import pymel.core as pm
from utils import strutils
from stage.apps.extract_core import ExtractCore
from stage.apps.maya import extract_infos

class Shader(ExtractCore):

    nice_name = "Shader"
    color = (255, 255, 255)
    propertys=['aiFrameOffset', 'aiSpecular', 'aiUseColorTemperature', 'aiShadowDensity', 'aiVisibleInSpecularReflection', 'aiOverrideDoubleSided', 'aiSss', 'aiMaxBounces', 'aiVisibleInVolume', 'aiMotionVectorSource', 'aiSubdivIterations', 'aiFrameNumber', 'doubleSided', 'aiVolume', 'aiTraceSets', 'aiDispAutobump', 'aiExportRefTangents', 'aiOverrideReceiveShadows', 'aiSelfShadows', 'aiDispHeight', 'aiOverrideLightLinking', 'aiOpaque', 'aiSubdivSmoothDerivs', 'aiColorTemperature', 'aiOverrideMatte', 'aiExportRefPoints', 'aiExposure', 'aiVisibleInSpecularTransmission', 'aiDiffuse', 'castsShadows', 'aiVolumePadding', 'smoothShading', 'aiExportColors', 'aiIndirect', 'visibleInReflections', 'aiSubdivPixelError', 'aiOverrideShaders', 'aiDispZeroValue', 'aiVisibleInDiffuseReflection', 'aiNamespace', 'aiSamples', 'aiShadowColor', 'opposite', 'motionBlur', 'aiSssSetname', 'aiSubdivFrustumIgnore', 'aiSubdivUvSmoothing', 'aiShadowColorR', 'aiFilters', 'aiUseSubFrame', 'aiTranslator', 'visibleInRefractions', 'aiOverrideNodes', 'aiExportRefNormals', 'aiSubdivAdaptiveMetric', 'aiCastVolumetricShadows', 'aiOverrideSelfShadows', 'aiUserOptions', 'aiDispPadding', 'aiSubdivType', 'aiMatte', 'primaryVisibility', 'receiveShadows', 'aiAov', 'aiExportTangents', 'aiShadowColorG', 'aiUseFrameExtension', 'aiNormalize', 'aiShadowColorB', 'aiVolumeSamples', 'aiVisibleInDiffuseTransmission', 'aiMotionVectorUnit', 'aiMotionVectorScale', 'aiSubdivAdaptiveSpace', 'aiAutobumpVisibility', 'aiToonId', 'holdOut', 'aiCastShadows', 'aiStepSize', 'aiOverrideOpaque']

    def __init__(self):
        super(Shader, self).__init__()
        om.MGlobal.displayInfo("Shader Extractor loaded")

        self._extension = ".shader"
        self.extension_second="_shader.ma"


    def _extract_default(self):

        _file_path = self.resolve_output()

        srf_dict = {}
        sg_list = []
        for sg in pm.ls(type='shadingEngine'):
            if sg in ['initialParticleSE', 'initialShadingGroup']:
                continue
            sg_list.append(sg)
            meshs = self.get_members(sg.name())

            if not meshs:
                continue

            for mesh in meshs:

                face_set = None
                surface_shader = None
                displacement_shader = None
                if isinstance(mesh, list):
                    shape = mesh[0]
                    face_set = str(mesh[1])
                else:
                    shape = mesh

                if sg.attr('surfaceShader').connections():
                    surface_shader = sg.attr('surfaceShader').connections()[0].name()

                if sg.attr('ds').connections():
                    displacement_shader = sg.attr('ds').connections()[0].name()

                sgs = {
                    sg.name(): {
                        "faceSet": face_set,
                        "shaders": {
                            "displacementShader": displacement_shader,
                            "surfaceShader": surface_shader
                        }
                    }
                }
                # print(shape,srf_dict)
                if shape in srf_dict.keys():
                    try:
                        srf_dict[shape]["sgs"] |= sgs
                    except:
                        srf_dict[shape]["sgs"].update(sgs)
                else:
                    srf_dict[shape] = {"sgs": sgs}

                shape_node = pm.PyNode(shape)

                srf_dict[shape]["propertys"]={}
                for property in self.propertys:
                    srf_dict[shape]["propertys"][property]=shape_node.attr(property).get()


        with  open(_file_path, 'w') as f:
            f.write(json.dumps(srf_dict, indent=4))

        shader_file = self.resolve_output_second()

        pm.select(sg_list, r=True, ne=True)
        pm.exportSelected(shader_file, force=True, options="v=0;", type="mayaAscii", pr=True, es=True)
        self.extract_json[self.__class__.name].update(extract_infos.get_extract_infos(_file_path))
        self.extract_json[self.__class__.name].update(extract_infos.get_extract_infos(shader_file))


    def get_members(self,sel):
        ret = []
        list = om.MSelectionList()
        list.add(sel)
        obj = list.getDependNode(0)
        grp = om.MFnSet(obj)
        members = grp.getMembers(True)

        for i in range(members.length()):

            __, vertices = members.getComponent(i)
            if vertices.isNull():
                if members.getDagPath(i).fullPathName() != '|shaderBallGeom1|shaderBallGeomShape1':
                    ret.append(members.getDagPath(i).fullPathName())
            else:
                fn_vertices = om.MFnSingleIndexedComponent(vertices)

                vertex_indices = fn_vertices.getElements()
                ret.append([members.getDagPath(i).fullPathName(), [v for v in vertex_indices]])
        return ret