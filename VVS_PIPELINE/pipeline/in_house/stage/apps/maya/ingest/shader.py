"""Ingest shader file."""

from pathlib import Path
import json
from maya import cmds
import pymel.core as pm
from maya import OpenMaya as om
from stage.apps.ingest_core import IngestCore


class Shader(IngestCore):
    """Ingest Shader Maya File."""

    nice_name = "Ingest Shader File"
    valid_extensions = [".shader"]
    referencable = True

    def __init__(self):
        super(Shader, self).__init__()

    def load_shader(self,name_space,shader_name_space):

        with open(self.ingest_path, 'r') as data:
            data = json.load(data)

            for shaper in data.keys():

                sgs = data[shaper]['sgs']
                propertys = data[shaper]['propertys']

                if not pm.objExists(shaper):
                    regx = r'\|' + r'\|'.join(fr'{name_space}\d*:{p}' for p in shaper.split('|')[1:])
                    shape_names = pm.ls(regex=regx)

                    if not shape_names:
                        pm.displayWarning(regx)
                        pm.displayWarning(u'未发现mesh:%s' % shaper)
                        continue

                    shapers = [shape_name.longName() for shape_name in shape_names]
                else:
                    shapers = [shaper]

                for sg in sgs.keys():
                    sg_full_name = shader_name_space + ':' + sg
                    face_set = sgs[sg]['faceSet']
                    sg = pm.PyNode(sg_full_name)

                    for shape_name in shapers:

                        if face_set:
                            face_list = face_set.replace('[', '').replace(']', '').split(',')
                            shape_names = [shape_name + '.f[' + f + ']' for f in face_list]
                            pm.sets(sg, e=True, forceElement=shape_names)
                        else:
                            pm.sets(sg, e=True, forceElement=shape_name)

                        shaper_node = pm.PyNode(shape_name)
                        for prp in propertys.keys():
                            shaper_node.attr(prp).set(propertys[prp])



    def _bring_in_default(self):
        """Import the Maya Shader file."""
        self._reference_default()
        # om.MGlobal.displayInfo("Bringing in Shader file")
        # cmds.file(self.ingest_path.as_posix().replace('.shader','_shader.ma'), i=True)


    def _reference_default(self):
        """Reference the Maya Shader file."""

        om.MGlobal.displayInfo("Referencing Shader File")

        if self.parameter:
            func = self.parameter.get(self.__class__.__name__.lower()).get('name_space')
            name_space = func(Path(self.ingest_path).stem)
        else:
            name_space = Path(self.ingest_path).stem

        ref = cmds.file(
            self.ingest_path.as_posix().replace('.shader','_shader.ma'),
            reference=True,
            groupLocator=True,
            mergeNamespacesOnClash=False,
            namespace= Path(self.ingest_path).stem,
            returnNewNodes=True,
        )
        self.load_shader(name_space,Path(self.ingest_path).stem)
        return ref
