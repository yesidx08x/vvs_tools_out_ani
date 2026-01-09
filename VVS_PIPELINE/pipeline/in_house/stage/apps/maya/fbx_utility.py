
from pathlib import Path
from maya import cmds
from maya import mel

import_settings = {
    "merge_mode": "FBXImportMode -v {}",  # add, merge, exmerge, exmergekeyedxforms
    "smoothing_groups": "FBXProperty Import|IncludeGrp|Geometry|SmoothingGroups -v {}",  # False
    "unlock_normals": "FBXProperty Import|IncludeGrp|Geometry|UnlockNormals -v {}",  # False
    "combine_per_vertex_normals": "FBXProperty Import|IncludeGrp|Geometry|HardEdges -v {}",  # False
    "animation": "FBXProperty Import|IncludeGrp|Animation -v {}",  # True
    # We are not adding animation take here because it needs to declared in the import command directly
    "fill_timeline": "FBXProperty Import|IncludeGrp|Animation|ExtraGrp|TimeLine -v {}",  # False
    "bake_animation_layers": "FBXProperty Import|IncludeGrp|Animation|ExtraGrp|BakeAnimationLayers -v {}",  # True
    "optical_markers": "FBXProperty Import|IncludeGrp|Animation|ExtraGrp|Markers -v {}",  # False
    "quaternion_interpolation_mode": 'FBXProperty Import|IncludeGrp|Animation|ExtraGrp|Quaternion -v "{}"',  # 'resample'
    "protect_driven_keys": "FBXProperty Import|IncludeGrp|Animation|ExtraGrp|ProtectDrivenKeys -v {}",  # False
    "deform_elements_to_joints": "FBXProperty Import|IncludeGrp|Animation|ExtraGrp|DeformNullsAsJoints -v {}",  # True
    "update_pivots_from_nulls": "FBXProperty Import|IncludeGrp|Animation|ExtraGrp|NullsToPivot -v {}",  # True
    "geometry_cache": "FBXProperty Import|IncludeGrp|Animation|ExtraGrp|PointCache -v {}",  # True
    "deformed_models": "FBXProperty Import|IncludeGrp|Animation|Deformation -v {}",  # True
    "skins": "FBXProperty Import|IncludeGrp|Animation|Deformation|Skins -v {}",  # True
    "blend_shapes": "FBXProperty Import|IncludeGrp|Animation|Deformation|Shape -v {}",  # True
    "pre_normalize_weights": "FBXProperty Import|IncludeGrp|Animation|Deformation|ForceWeightNormalize -v {}",  # False
    "constraints": "FBXProperty Import|IncludeGrp|Animation|ConstraintsGrp|Constraint -v {}",  # True
    "skeleton_definition_as": 'FBXProperty Import|IncludeGrp|Animation|ConstraintsGrp|CharacterType -v "{}"',  # 'HumanIK'
    "cameras": "FBXProperty Import|IncludeGrp|CameraGrp|Camera -v {}",  # True
    "lights": "FBXProperty Import|IncludeGrp|LightGrp|Light -v {}",  # True
    "audio": "FBXProperty Import|IncludeGrp|Audio -v {}",  # True
    "automatic_scale_factor": "FBXProperty Import|AdvOptGrp|UnitsGrp|DynamicScaleConversion -v {}",  # True
    "file_units_converted_to": 'FBXProperty Import|AdvOptGrp|UnitsGrp|UnitsSelector -v "{}"',  # 'Centimeters'
    "show_warnings_manager": "FBXProperty Import|AdvOptGrp|UI|ShowWarningsManager -v {}",  # False
    "generate_log_data": "FBXProperty Import|AdvOptGrp|UI|GenerateLogData -v {}",  # False
    "remove_bad_polygons": "FBXProperty Import|AdvOptGrp|Performance|RemoveBadPolysFromMesh -v {}",  # True
    "blind_data": "FBXProperty Import|IncludeGrp|Geometry|BlindData -v {}",  # False
    "curve_filter": "FBXProperty Import|IncludeGrp|Animation|CurveFilter -v {}",  # False
    "sampling_rate_selector": 'FBXProperty Import|IncludeGrp|Animation|SamplingPanel|SamplingRateSelector -v "{}"',  # Scene (Scene, File, Custom)
    "curve_filter_sampling_rate": "FBXProperty Import|IncludeGrp|Animation|SamplingPanel|CurveFilterSamplingRate -v {}",  # 24
    "axis_conversion": "FBXProperty Import|AdvOptGrp|AxisConvGrp|AxisConversion -v {}",  # False
    "up_axis": 'FBXProperty Import|AdvOptGrp|AxisConvGrp|UpAxis -v "{}"',  # 'Y'
}

export_settings = {
    "smoothing_groups": "FBXProperty Export|IncludeGrp|Geometry|SmoothingGroups -v {}",  # False
    "split_per_vertex_normals": "FBXProperty Export|IncludeGrp|Geometry|expHardEdges -v {}",  # False
    "tangents_and_binormals": "FBXProperty Export|IncludeGrp|Geometry|TangentsandBinormals -v {}",  # False
    "smooth_mesh": "FBXProperty Export|IncludeGrp|Geometry|SmoothMesh -v {}",  # True
    "selection_sets": "FBXProperty Export|IncludeGrp|Geometry|SelectionSet -v {}",  # False
    "convert_to_null_objects": "FBXProperty Export|IncludeGrp|PivotToNulls -v {}",  # False
    "preserve_instances": "FBXProperty Export|IncludeGrp|Geometry|Instances -v {}",  # False
    "referenced_assets_content": "FBXProperty Export|IncludeGrp|Geometry|ContainerObjects -v {}",  # True
    "triangulate": "FBXProperty Export|IncludeGrp|Geometry|Triangulate -v {}",  # False
    "convert_nurbs_surface_to": 'FBXProperty Export|IncludeGrp|Geometry|GeometryNurbsSurfaceAs -v "{}"',  # 'Nurbs'
    "animation": "FBXProperty Export|IncludeGrp|Animation -v {}",  # True
    "use_scene_name": "FBXProperty Export|IncludeGrp|Animation|ExtraGrp|UseSceneName -v {}",  # False
    "remove_single_key": "FBXProperty Export|IncludeGrp|Animation|ExtraGrp|RemoveSingleKey -v {}",  # False
    "quaternion_interpolation_mode": 'FBXProperty Export|IncludeGrp|Animation|ExtraGrp|Quaternion -v "{}"',  # 'Resample'
    "bake_animation": "FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation -v {}",  # False
    "bake_start": "FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameStart -v {}",  # 0
    "bake_end": "FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameEnd -v {}",  # 200
    "bake_step": "FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameStep -v {}",  # 1
    "bake_resample_all": "FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|ResampleAnimationCurves -v {}",  # False
    "hide_complex_animation_warning": "FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|HideComplexAnimationBakedWarning -v {}",  # True
    "deformed_models": "FBXProperty Export|IncludeGrp|Animation|Deformation -v {}",  # True
    "skins": "FBXProperty Export|IncludeGrp|Animation|Deformation|Skins -v {}",  # True
    "blend_shapes": "FBXProperty Export|IncludeGrp|Animation|Deformation|Shape -v {}",  # True
    "shape_attributes": "FBXProperty Export|IncludeGrp|Animation|Deformation|ShapeAttributes -v {}",  # False
    "attribute_values": 'FBXProperty Export|IncludeGrp|Animation|Deformation|ShapeAttributes|ShapeAttributesValues -v "{}"',  # 'Relative'
    "curve_filters": "FBXProperty Export|IncludeGrp|Animation|CurveFilter -v {}",  # False
    "constant_key_reducer": "FBXProperty Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed -v {}",  # False
    "translation_precision": "FBXProperty Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|CurveFilterCstKeyRedTPrec -v {}",  # 0.0001
    "rotation_precision": "FBXProperty Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|CurveFilterCstKeyRedRPrec -v {}",  # 0.0090
    "scaling_precision": "FBXProperty Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|CurveFilterCstKeyRedSPrec -v {}",  # 0.0040
    "other_precision": "FBXProperty Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|CurveFilterCstKeyRedOPrec -v {}",  # 0.0090
    "auto_tangents_only": "FBXProperty Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|AutoTangentsOnly -v {}",  # True
    "geometry_cache": "FBXProperty Export|IncludeGrp|Animation|PointCache -v {}",  # False
    "geometry_cache_set": 'FBXProperty Export|IncludeGrp|Animation|PointCache|SelectionSetNameAsPointCache -v "{}"',  # " "
    "constraints": "FBXProperty Export|IncludeGrp|Animation|ConstraintsGrp|Constraint -v {}",  # False
    "skeleton_definitions": "FBXProperty Export|IncludeGrp|Animation|ConstraintsGrp|Character -v {}",  # False
    "cameras": "FBXProperty Export|IncludeGrp|CameraGrp|Camera -v {}",  # True
    "lights": "FBXProperty Export|IncludeGrp|LightGrp|Light -v {}",  # True
    "audio": "FBXProperty Export|IncludeGrp|Audio -v {}",  # True
    "embed_media": "FBXProperty Export|IncludeGrp|EmbedTextureGrp|EmbedTexture -v {}",  # False
    "include_children": "FBXProperty Export|IncludeGrp|InputConnectionsGrp|IncludeChildren -v {}",  # True
    "input_connections": "FBXProperty Export|IncludeGrp|InputConnectionsGrp|InputConnections -v {}",  # True
    "automatic_scale_factor": "FBXProperty Export|AdvOptGrp|UnitsGrp|DynamicScaleConversion -v {}",  # True
    "file_units_converted_to": 'FBXProperty Export|AdvOptGrp|UnitsGrp|UnitsSelector -v "{}"',  # 'cm'
    "up_axis": 'FBXProperty Export|AdvOptGrp|AxisConvGrp|UpAxis -v "{}"',  # 'Y'
    "show_warning_manager": "FBXProperty Export|AdvOptGrp|UI|ShowWarningsManager -v {}",  # False
    "generate_log_data": "FBXProperty Export|AdvOptGrp|UI|GenerateLogData -v {}",  # False
    "animation_only": "FBXProperty Export|IncludeGrp|Geometry|AnimationOnly -v {}",  # False
    "blind_data": "FBXProperty Export|IncludeGrp|Geometry|BlindData -v {}",  # True
    "bind_pose": "FBXProperty Export|IncludeGrp|BindPose -v {}",  # True
    "bypass_rss_inheritance": "FBXProperty Export|IncludeGrp|BypassRrsInheritance -v {}",  # False
}


def reset_import_settings():
    """Reset import settings to default"""
    mel.eval("FBXResetImport")


def reset_export_settings():
    """Reset import settings to default"""
    mel.eval("FBXResetExport")


def _format(value):
    """Format value for mel command"""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return value


def _set_fbx_settings(**kwargs):
    """Build FBX import settings"""
    for key, value in kwargs.items():
        value = _format(value)
        if key in import_settings.keys():
            cmd = import_settings[key].format(value)
            mel.eval(cmd)


def _import_fbx(file_path, take=-1):
    """Import FBX file."""
    file_path = file_path.as_posix().replace("\\", "//")  ## for compatibility with mel syntax.
    import_cmd = 'FBXImport -f "{0}" -t {1};'.format(file_path, take)
    mel.eval(import_cmd)


def _export_fbx(file_path, selected=False):
    """Export FBX file."""
    s_flag = " -s" if selected else ""
    file_path = file_path.replace("\\", "//")  ## for compatibility with mel syntax.
    export_cmd = 'FBXExport -f "{0}"{1};'.format(file_path, s_flag)
    mel.eval(export_cmd)


def load(
    file_path,
    merge_mode="merge",  # add, merge, exmergem, exmergekeyedxforms
    namespace=None,
    smoothing_groups=False,
    unlock_normals=False,
    combine_per_vertex_normals=False,
    animation=True,
    take=-1,
    fill_timeline=False,
    bake_animation_layers=True,
    optical_markers=False,
    quaternion_interpolation_mode="resample",
    protect_driven_keys=False,
    deform_elements_to_joints=True,
    update_pivots_from_nulls=True,
    geometry_cache=True,
    deformed_models=True,
    skins=True,
    blend_shapes=True,
    pre_normalize_weights=False,
    constraints=True,
    skeleton_definition_as="HumanIK",  # 'HumanIK', 'None'
    cameras=True,
    lights=True,
    audio=True,
    automatic_scale_factor=True,
    file_units_converted_to="Centimeters",  # 'Centimeters', 'Meters', 'Inches', 'Feet', 'Yards', 'Miles', 'Millimeters', 'Kilometers'
    show_warnings_manager=False,
    generate_log_data=False,
    remove_bad_polygons=True,
    blind_data=False,
    curve_filter=False,
    sampling_rate_selector="Scene",  # 'Scene' , 'File', 'Custom')
    curve_filter_sampling_rate=24,
    axis_conversion=False,
    up_axis="Y",  # 'Y', 'Z'
):

    quaternion_interpolation_mode = {
        "resample": "Resample As Euler Interpolation",
        "euler": "Set As Euler Interpolation",
        "quaternion": "Retain Quaternion Interpolation",
    }.get(quaternion_interpolation_mode, "Resample As Euler Interpolation")
    reset_import_settings()
    if namespace:
        if not cmds.namespace(exists=namespace):
            cmds.namespace(addNamespace=namespace)
        cmds.namespace(setNamespace=namespace)

    _set_fbx_settings(**locals())

    # file_path = file_path.replace("\\", "//")  ## for compatibility with mel syntax.
    # import_cmd = ('FBXImport -f "{0}" -t {1};'.format(file_path, take))
    # grab a list of nodes before importing
    nodes_before = cmds.ls()

    _import_fbx(file_path, take=take)
    if namespace:
        cmds.namespace(setNamespace=":")
    # mel.eval(import_cmd)
    # grab a list of nodes after importing
    nodes_after = cmds.ls()
    # get the difference between the two lists
    imported_nodes = list(set(nodes_after) - set(nodes_before))
    return imported_nodes


def save(
    file_path,
    force=False,
    selection_only=False,
    smoothing_groups=False,
    split_per_vertex_normals=False,
    tangents_and_binormals=False,
    smooth_mesh=True,
    selection_sets=False,
    convert_to_null_objects=False,
    preserve_instances=False,
    referenced_assets_content=True,
    triangulate=False,
    convert_nurbs_surface_to="nurbs",
    animation=True,
    use_scene_name=False,
    remove_single_key=False,
    quaternion_interpolation_mode="resample",
    bake_animation=False,
    bake_start=0,
    bake_end=200,
    bake_step=1,
    bake_resample_all=False,
    hide_complex_animation_warning=True,
    deformed_models=True,
    skins=True,
    blend_shapes=True,
    shape_attributes=False,
    attribute_values="Relative",  # Relative, Absolute
    curve_filters=False,
    constant_key_reducer=False,
    translation_precision=0.0001,
    rotation_precision=0.009,
    scaling_precision=0.004,
    other_precision=0.009,
    auto_tangents_only=True,
    geometry_cache=False,
    geometry_cache_set=" ",
    constraints=False,
    skeleton_definitions=False,
    cameras=True,
    lights=True,
    audio=True,
    embed_media=False,
    include_children=True,
    input_connections=True,
    automatic_scale_factor=True,
    file_units_converted_to="Centimeters",  # Centimeters, Meters, Millimeters, Kilometers, Inches, Feet, Yards, Miles
    up_axis="Y",  # Y, Z
    show_warning_manager=False,
    generate_log_data=False,
    animation_only=False,
    blind_data=True,
    bind_pose=True,
    bypass_rss_inheritance=False,
):

    # check if the file exists
    if Path(file_path).exists() and not force:
        raise RuntimeError("File already exists: {}".format(file_path))
    convert_nurbs_surface_to = {
        "nurbs": "NURBS",
        "display": "Interactive Display Mesh",
        "render": "Software Render Mesh",
    }.get(convert_nurbs_surface_to, "NURBS")

    quaternion_interpolation_mode = {
        "resample": "Resample As Euler Interpolation",
        "euler": "Set As Euler Interpolation",
        "quaternion": "Retain Quaternion Interpolation",
    }.get(quaternion_interpolation_mode, "Resample As Euler Interpolation")

    reset_export_settings()
    # create a copy of the locals() dictionary
    settings_dict = locals().copy()
    # remove the selection_only argument
    settings_dict.pop("selection_only")
    settings_dict.pop("force")

    _set_fbx_settings(**settings_dict)

    _export_fbx(file_path, selected=selection_only)
    return file_path


