# XGEN_to_UE.py

from Qt.QtWidgets import QFrame, QDialog, QVBoxLayout, QHBoxLayout, \
    QPushButton, QLineEdit, QWidget, QLabel, QSpinBox, QComboBox, QCheckBox, \
    QFileDialog, QApplication
from Qt import QtCore

from maya import cmds, mel, OpenMaya
import xgenm as xg


# mel.eval('source "xgen.mel"; xgen()')

# UTILS -----------------------------------------------------------------------------------
def geometry_instancer_to_interactive_grooming(descriptions, prefix=None):
    if prefix:
        interactive_descriptions = cmds.xgmGroomConvert(descriptions, prefix=prefix)
    else:
        interactive_descriptions = cmds.xgmGroomConvert(descriptions)
    return cmds.listRelatives(interactive_descriptions, parent=True)


def rebuildHair(base):
    cmds.xgmRebuildSplineDescription(base, cv=cmds.getAttr('{0}.cvCount'.format(base)))


def query_shape(obj):
    try:
        shp = cmds.listRelatives(obj, c=True)[0]
    except:
        raise ValueError('Can\'t find description\'s shape for {}'.format(obj))
    return shp


def query_base(shp):
    try:
        base = cmds.listConnections('{}.inSplineData'.format(shp))[0]
    except:
        raise ValueError('Can\'t find splineBase for {}'.format(shp))
    return base


def convert_to_descriptions(xgen_insts):
    # xgen_insts = cmds.ls(sl=True, tr=True)
    for xgen_inst in xgen_insts:
        cmds.setAttr('{}.v'.format(xgen_inst), 1)
    descriptions = geometry_instancer_to_interactive_grooming(xgen_insts)
    cmds.hide(xgen_insts)
    return xgen_insts, descriptions


def export_description_to_alembic(description, file_path):
    command = '-file "{}"'.format(file_path)
    command += ' -df ogawa'
    command += ' -fr 1 1'
    command += ' -wfw'
    command += ' -obj {}'.format(description)
    cmds.xgmSplineCache(export=True, j=command)


def extract_guide_curves(xgen_inst):
    guidesName = xg.descriptionGuides(xgen_inst)
    cmds.select(guidesName, r=True)
    curves = mel.eval('xgmCreateCurvesFromGuidesOption(0, 0, "{}_curves")'.format(xgen_inst))


def create_guide_attr():
    attr_name = 'groom_guide'
    curves = cmds.listRelatives('xgGroom', ad=True, type='nurbsCurve')
    guides_group = cmds.createNode('transform', name='guides')
    # Add width attr
    # for crv in curves:
    #     cmds.addAttr(crv, longName='width', attributeType='short', defaultValue=.1, keyable=True)
    # tag group as groom_guide
    cmds.addAttr(guides_group, longName=attr_name, attributeType='short', defaultValue=1, keyable=True)
    # forces Maya's alembic to export curves as one group.
    cmds.addAttr(guides_group, longName='riCurves', attributeType='bool', defaultValue=1, keyable=True)
    # forces Maya's alembic to export data as GeometryScope::kConstantScope
    cmds.addAttr(guides_group, longName='{}_AbcGeomScope'.format(attr_name), dataType='string', keyable=True)
    cmds.setAttr('{}.{}_AbcGeomScope'.format(guides_group, attr_name), 'con', type='string')
    # parent curves under guides group
    for curve in curves:
        cmds.parent(curve, guides_group, shape=True, relative=True)
    # Clean-up
    cmds.delete('xgGroom')


def find_closest_uv_point(points, mesh_node, uv_set='map1'):
    # check mesh
    if not cmds.objExists(mesh_node):
        raise RuntimeError('Node not found: "{}"'.format(mesh_node))
    # check uv_set
    uv_sets = cmds.polyUVSet(mesh_node, q=True, allUVSets=True)
    if uv_set not in uv_sets:
        raise RuntimeError('Invalid uv_set provided: "{}"'.format(uv_set))
    # get mesh as dag-path
    selection_list = OpenMaya.MSelectionList()
    selection_list.add(mesh_node)
    mesh_dagpath = OpenMaya.MDagPath()
    selection_list.getDagPath(0, mesh_dagpath)
    mesh_dagpath.extendToShape()
    # get mesh function set
    fn_mesh = OpenMaya.MFnMesh(mesh_dagpath)
    uvs = list()
    for i in range(len(points)):
        script_util = OpenMaya.MScriptUtil()
        script_util.createFromDouble(0.0, 0.0)
        uv_point = script_util.asFloat2Ptr()
        point = OpenMaya.MPoint(*points[i])
        fn_mesh.getUVAtPoint(point, uv_point, OpenMaya.MSpace.kWorld, uv_set)
        u = OpenMaya.MScriptUtil.getFloat2ArrayItem(uv_point, 0, 0)
        v = OpenMaya.MScriptUtil.getFloat2ArrayItem(uv_point, 0, 1)
        uvs.append((u, v))
    return uvs


def create_root_uv_attribute(curves_group, mesh_node, uv_set='map1'):
    # check curves group
    if not cmds.objExists(curves_group):
        raise RuntimeError('Group not found: "{}"'.format(curves_group))
    # get curves in group
    curve_shapes = cmds.listRelatives(curves_group, shapes=True, noIntermediate=True)
    curve_shapes = cmds.ls(curve_shapes, type='nurbsCurve')
    if not curve_shapes:
        raise RuntimeError('Invalid curves group. No nurbs-curves found in group.')
    else:
        print("found curves")
        print(curve_shapes)
    # get curve roots
    points = list()
    for curve_shape in curve_shapes:
        point = cmds.pointPosition('{}.cv[0]'.format(curve_shape), world=True)
        points.append(point)
    # get uvs
    values = list()
    uvs = find_closest_uv_point(points, mesh_node, uv_set=uv_set)
    for u, v in uvs:
        values.append([u, v, 0])
    # create attribute
    name = 'groom_root_uv'
    cmds.addAttr(curves_group, ln=name, dt='vectorArray')
    cmds.addAttr(curves_group, ln='{}_AbcGeomScope'.format(name), dt='string')
    cmds.addAttr(curves_group, ln='{}_AbcType'.format(name), dt='string')

    cmds.setAttr('{}.{}'.format(curves_group, name), len(values), *values, type='vectorArray')
    cmds.setAttr('{}.{}_AbcGeomScope'.format(curves_group, name), 'uni', type='string')
    cmds.setAttr('{}.{}_AbcType'.format(curves_group, name), 'vector2', type='string')

    print('UV ATTR ADDED')
    # return uvs


def abc_export(file_path, splines_grp):
    start_frame = int(cmds.playbackOptions(q=True, minTime=True))
    end_frame = int(cmds.playbackOptions(q=True, maxTime=True))
    command = '-file "{}"'.format(file_path)
    command += ' -df ogawa'
    command += ' -fr {} {}'.format(start_frame, end_frame)
    command += ' -stripNamespaces'
    command += ' -uvWrite'
    command += ' -worldSpace'
    command += ' -writeColorSets'  # writeColorSets
    command += ' -writeUVSets'  # writeUVSets
    command += ' -attr groom_root_uv'
    command += ' -attr groom_group_id'
    command += ' -attr groom_guide'
    command += ' -root {}'.format(splines_grp)
    print(command)
    cmds.AbcExport(verbose=False, j=command)


def list_attributes(splines_grp):
    nodes = cmds.listRelatives(splines_grp, c=True)
    for node in nodes:
        print('--- %s ----' % node)
        for attr in cmds.listAttr(node):
            print(attr)


def list_scene_meshes():
    return [cmds.listRelatives(x, p=True)[0] for x in cmds.ls(type='mesh')]


def list_scene_XGen_instances():
    guides = cmds.ls(type='xgmSplineGuide')
    descriptions = set()
    for guide in guides:
        descriptions.add(
            cmds.listRelatives(cmds.listRelatives(cmds.listRelatives(guide, p=True)[0], p=True)[0], p=True)[0])
    return descriptions


# CLASSES ---------------------------------------------------------------------------------
class Grooms():
    def __init__(self, descriptions):
        self.descriptions = descriptions
        #
        self.shapes = {}
        self.bases = {}
        self.insts = {}
        self.cache_paths = {}
        self.spline_objs = {}
        #
        self.id_lines = {}
        #
        self.uv_mesh = None
        #
        self.spline_grp = 'grp_hair'
        #
        self.add_shapes_and_bases()

    def add_inst(self, description, xgen_inst):
        self.insts[description] = xgen_inst

    def add_shapes_and_bases(self):
        for description in self.descriptions:
            self.shapes[description] = query_shape(description)
            self.bases[description] = query_base(description)

    def add_cache_paths(self, cache_dir):
        for desc in self.descriptions:
            self.cache_paths[desc] = '{0}/{1}.abc'.format(cache_dir, desc)


# -------------------------------------------------
class XGen_to_UE_UI(QDialog):
    def __init__(self):
        self.close_existing_window()
        super().__init__()

        self.grooms = None
        self.id_line_wgts = []

        self.initGUI()
        self.init_signals()

    def close_existing_window(self):
        for qt in QApplication.topLevelWidgets():
            try:
                if qt.__class__.__name__ == self.__class__.__name__:
                    qt.close()
            except:
                pass

    def initGUI(self):
        self.setWindowTitle('XGen to UE plus')
        self.setGeometry(300, 300, 120, 200)
        self.setFixedWidth(500)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setLayout(QVBoxLayout())
        set_margins_spacing_alignment(self, (2, 2, 2, 2), 2, 'Top')
        #
        Center_LB('Pick UV mesh', self)
        self.uv_mesh_cb = QComboBox()
        self.uv_mesh_cb.addItems(list_scene_meshes())
        self.layout().addWidget(self.uv_mesh_cb)
        #
        Center_LB('Instances to Convert', self)
        self.xgen_instances_wgt = XGen_Instances_Widget(self)
        #
        self.convert_to_descriptions_btn = QPushButton('Convert to Descriptions')
        self.layout().addWidget(self.convert_to_descriptions_btn)
        #
        self.rebuild_base_btn = QPushButton('Rebuild Base')

        #self.layout().addWidget(self.rebuild_base_btn)

        #
        self.create_guides_attr_btn = QPushButton('Create Guides')
        #self.layout().addWidget(self.create_guides_attr_btn)


        #
        self.process_descriptions_export_btn = QPushButton('Process descriptions ( Export ABC)')
        self.layout().addWidget(self.process_descriptions_export_btn)



        self.create_nhair_attr_btn = QPushButton('Create nHair')
        self.layout().addWidget(self.create_nhair_attr_btn)

        Splitter(self)

        #
        self.process_descriptions_import_btn = QPushButton('Process descriptions ( Import ABC)')
        #self.layout().addWidget(self.process_descriptions_import_btn)
        #
        self.create_uv_attr_btn = QPushButton('UV attr')
        self.layout().addWidget(self.create_uv_attr_btn)
        #
        self.id_attr_table_wgt = Widget_Layout(self, direction='V')
        # self.id_attr_table_wgt.setLayout(QVBoxLayout())
        # self.layout().addWidget(self.id_attr_table_wgt)
        self.create_id_attr_btn = QPushButton('ID attr')
        self.layout().addWidget(self.create_id_attr_btn)
        #
        self.create_guid_attr_btn = QPushButton('GUID attr')
        self.layout().addWidget(self.create_guid_attr_btn)
        #
        Splitter(self)
        self.export_abc_btn = QPushButton('Final Export (ABC)')
        self.layout().addWidget(self.export_abc_btn)
        #
        Splitter(self)
        self.lock_maya_btn = QPushButton('Lock Viewport')
        self.layout().addWidget(self.lock_maya_btn)
        self.unlock_maya_btn = QPushButton('Unlock Viewport')
        self.layout().addWidget(self.unlock_maya_btn)
        #
        Splitter(self)
        self.list_attributes_btn = QPushButton('Print Attributes')
        # self.layout().addWidget(self.list_attributes_btn)

    def init_signals(self):
        self.convert_to_descriptions_btn.clicked.connect(self.convert_to_descriptions)
        self.rebuild_base_btn.clicked.connect(self.rebuild_bases)
        self.process_descriptions_export_btn.clicked.connect(self.process_descriptions_export)
        self.process_descriptions_import_btn.clicked.connect(self.process_descriptions_import)
        self.create_guides_attr_btn.clicked.connect(self.create_guides)
        self.create_nhair_attr_btn.clicked.connect(self.create_nhair)
        self.create_uv_attr_btn.clicked.connect(self.add_uv_attr)
        self.create_id_attr_btn.clicked.connect(self.add_id_attr)
        self.create_guid_attr_btn.clicked.connect(self.add_guid_attr)

        self.export_abc_btn.clicked.connect(self.export_abc)

        self.lock_maya_btn.clicked.connect(self.lock_viewport)
        self.unlock_maya_btn.clicked.connect(self.unlock_viewport)

        self.list_attributes_btn.clicked.connect(self.list_attributes)

    # Methods
    def convert_to_descriptions(self):
        process_xgen_insts = [key for key, item in self.xgen_instances_wgt.xgen_insts.items() if item.isChecked()]
        xgen_insts, descriptions = convert_to_descriptions(process_xgen_insts)
        self.grooms = Grooms(descriptions)
        for description, xgen_inst in zip(descriptions, xgen_insts):
            self.grooms.add_inst(description, xgen_inst)
            self.grooms.id_lines[description] = Label_Spinbox(self.id_attr_table_wgt, description)
        # Check off interpolation
        for base in self.grooms.bases.values():
            cmds.setAttr('%s.interpolate' % base, 0)
        self.convert_to_descriptions_btn.setStyleSheet('QPushButton {color : rgb(25, 25, 25)}')

    def rebuild_bases(self):
        for base in self.grooms.bases.values():
            rebuildHair(base)
        self.rebuild_base_btn.setStyleSheet('QPushButton {color : rgb(25, 25, 25)}')

    def process_descriptions_export(self):
        cache_dir = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.grooms.add_cache_paths(cache_dir)
        # Group
        #cmds.group(em=True, n=self.grooms.spline_grp)
        # Export
        for description, file_path in self.grooms.cache_paths.items():
            export_description_to_alembic(description, file_path)

        self.process_descriptions_export_btn.setStyleSheet('QPushButton {color : rgb(25, 25, 25)}')
    def process_descriptions_import(self):
        # Import
        for description, file_path in self.grooms.cache_paths.items():
            cmds.AbcImport(file_path, mode='import')
            import_grp = '%s1' % description
            spline_objs = cmds.listRelatives(import_grp, c=True, pa=True)
            for spline_obj in spline_objs:
                cmds.parent(spline_obj, self.grooms.spline_grp)
                children = cmds.listRelatives(self.grooms.spline_grp, c=True, pa=True)
                for child in children:
                    if child not in self.grooms.spline_objs.keys():
                        self.grooms.spline_objs[child] = description
                        break
            cmds.delete(import_grp)
        if cmds.objExists('guides'):
            cmds.parent('guides', self.grooms.spline_grp)
    def create_guides(self):
        for xgen_inst in self.grooms.insts.values():
            extract_guide_curves(xgen_inst)
        create_guide_attr()
        self.create_guides_attr_btn.setStyleSheet('QPushButton {color : rgb(25, 25, 25)}')

    def create_nhair(self):
        for xgen_inst in self.grooms.insts.values():
            extract_guide_curves(xgen_inst)
        curves = cmds.listRelatives('xgGroom', ad=True, type='nurbsCurve')

        cmds.select(curves,r=1)
        cmds.select(self.uv_mesh_cb.currentText(), tgl=1)
        mel.eval('makeCurvesDynamic 2 { "1", "1", "1", "1", "0"};')


        hair_list = cmds.ls(type='hairSystem')
        for hair in hair_list:
            cmds.setAttr("{0}.simulationMethod".format(hair), 1)

        follicle_list = cmds.ls(type='follicle')
        for follicle in follicle_list:
            cmds.setAttr("{0}.simulationMethod".format(follicle), 0)

        self.create_nhair_attr_btn.setStyleSheet('QPushButton {color : rgb(25, 25, 25)}')

    def add_uv_attr(self):
        select_grp=cmds.ls(sl=1)[0]
        spline_objs = cmds.listRelatives(select_grp, c=True, pa=True)
        for spline_obj in spline_objs:
            create_root_uv_attribute(spline_obj, self.uv_mesh_cb.currentText())
        self.create_uv_attr_btn.setStyleSheet('QPushButton {color : rgb(25, 25, 25)}')

    def add_id_attr(self):
        attr_name = 'groom_group_id'
        groups = cmds.listRelatives(cmds.ls(sl=1)[0], c=1, f=1)
        for groom_group_id, group_name in enumerate(groups):
            # get curves under xgGroom
            curves = cmds.listRelatives(group_name, ad=True, type='nurbsCurve')

            # tag group with group id
            cmds.addAttr(group_name, longName=attr_name, attributeType='short', defaultValue=0,
                         keyable=True)

            # add attribute scope
            # forces Maya's alembic to export data as GeometryScope::kConstantScope
            cmds.addAttr(group_name, longName='{}_AbcGeomScope'.format(attr_name), dataType='string', keyable=True)
            cmds.setAttr('{}.{}_AbcGeomScope'.format(group_name, attr_name), 'con', type='string')
        print('ID ATTR ADDED')
        self.create_id_attr_btn.setStyleSheet('QPushButton {color : rgb(25, 25, 25)}')
    def add_guid_attr(self):
        attr_name = 'groom_guide'

        # get curves under xgGroom
        curves = cmds.listRelatives(cmds.ls(sl=1,l=1)[0],f=1, ad=True, type='nurbsCurve')

        # create new group
        guides_group = cmds.createNode('transform', name='guides')

        # tag group as groom_guide
        cmds.addAttr(guides_group, longName=attr_name, attributeType='short', defaultValue=1, keyable=True)

        # forces Maya's alembic to export curves as one group.
        cmds.addAttr(guides_group, longName='riCurves', attributeType='bool', defaultValue=1, keyable=True)

        # add attribute scope
        # forces Maya's alembic to export data as GeometryScope::kConstantScope
        cmds.addAttr(guides_group, longName='{}_AbcGeomScope'.format(attr_name), dataType='string', keyable=True)
        cmds.setAttr('{}.{}_AbcGeomScope'.format(guides_group, attr_name), 'con', type='string')

        # parent curves under guides group
        for curve in curves:
            cmds.parent(curve, guides_group, shape=True, relative=True)
        self.create_guid_attr_btn.setStyleSheet('QPushButton {color : rgb(25, 25, 25)}')
    def export_abc(self):
        file_path = QFileDialog.getSaveFileName(self, "Save File", filter='*.abc')[0]
        abc_export(file_path, ' -root '.join(cmds.ls(sl=1,l=1)))
        print('Exported to: %s' % file_path)

    def lock_viewport(self):
        cmds.refresh(suspend=True)

    def unlock_viewport(self):
        cmds.refresh(suspend=False)

    def list_attributes(self):
        list_attributes(self.grooms.spline_grp)


# UI utils
def set_margins_spacing_alignment(widget, margins, spacing, alignment=None):
    widget.layout().setContentsMargins(*margins)
    widget.layout().setSpacing(spacing)
    if alignment:
        widget.layout().setAlignment(eval('QtCore.Qt.Align%s' % alignment))


class XGen_Instances_Widget(QWidget):
    def __init__(self, parent, height=0, width=0, margins=(0, 0, 0, 0), alignment='Top'):
        super(XGen_Instances_Widget, self).__init__()

        self.xgen_insts = {}

        self.setLayout(QVBoxLayout())
        set_margins_spacing_alignment(self, margins, 4, alignment)
        if parent:
            parent.layout().addWidget(self)
        if height:
            self.setFixedHeight(height)
        if width:
            self.setFixedWidth(width)

        for inst in list_scene_XGen_instances():
            self.xgen_insts[inst] = QCheckBox(inst)
            self.xgen_insts[inst].setChecked(True)
            self.layout().addWidget(self.xgen_insts[inst])


class Label_Spinbox(QWidget):
    def __init__(self, parent, text):
        super().__init__()
        self.setLayout(QHBoxLayout())
        set_margins_spacing_alignment(self, (0, 0, 0, 0), 2)
        self.lb = QLabel(text)
        self.sb = QSpinBox()
        self.sb.setFixedWidth(60)
        self.layout().addWidget(self.lb)
        self.layout().addWidget(QFrame())
        self.layout().addWidget(self.sb)
        parent.layout().addWidget(self)


class Splitter(QFrame):
    def __init__(self, parent=None, direction='H', size=8, style='line'):
        QFrame.__init__(self)
        if direction == 'H':
            if style == 'line':
                self.setFrameStyle(QFrame.HLine)
            self.setFixedHeight(size)
        else:
            if style == 'line':
                self.setFrameStyle(QFrame.VLine)
            self.setFixedWidth(size)
        if parent:
            parent.layout().addWidget(self)


class Center_LB(QWidget):
    def __init__(self, text, parent=None):
        super(Center_LB, self).__init__()

        self.setLayout(QHBoxLayout())
        set_margins_spacing_alignment(self, (4, 4, 4, 4), 4, 'Top')
        Splitter(self)
        LB = QLabel(text)
        LB.setAlignment(QtCore.Qt.AlignCenter)
        self.layout().addWidget(LB)
        Splitter(self)
        if parent:
            parent.layout().addWidget(self)


class Widget_Layout(QWidget):
    def __init__(self, parent, *widgets, direction='H', height=0, width=0, margins=(0, 0, 0, 0), alignment='Top'):
        super(Widget_Layout, self).__init__()
        if direction == 'H':
            self.setLayout(QHBoxLayout())
        else:
            self.setLayout(QVBoxLayout())
        set_margins_spacing_alignment(self, margins, 4, alignment)
        if parent:
            parent.layout().addWidget(self)

        if height:
            self.setFixedHeight(height)
        if width:
            self.setFixedWidth(width)

        for wgt in widgets:
            self.layout().addWidget(wgt)


# ACTIVATE UI
dialog = None


def create_UI():
    global dialog

    dialog = XGen_to_UE_UI()
    dialog.show()
    return dialog


def delete_UI():
    global dialog
    if dialog is None:
        return
    dialog.deleteLater()
    dialog = None


def main():
    return create_UI()

if __name__=='__main__':
    main()
