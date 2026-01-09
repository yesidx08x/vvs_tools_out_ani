import maya.cmds as cmds
from stage.common.utils import calculate_md5, get_current_time, get_file_size
from stage.apps.maya.utils import get_ranges, get_scene_fps


def get_extract_infos(output_file, full_path_name=None):
    ref_file = ''

    start_frame, _, _, end_frame = get_ranges()
    if full_path_name:
        if cmds.referenceQuery(full_path_name, isNodeReferenced=True):
            ref_file = cmds.referenceQuery(full_path_name, filename=True, withoutCopyNumber=True)
            type = "reference"
        else:
            type = cmds.nodeType(full_path_name)
    else:
        type = ''

    struct = {'ref_file': ref_file,
              'type': type,
              'ref_file_md5': calculate_md5(ref_file) if ref_file else '',
              'name': full_path_name,
              'fps': get_scene_fps(),
              'start_frame': start_frame,
              'end_frame': end_frame,
              'output_file': output_file,
              'file_size': get_file_size(output_file),
              'time': get_current_time(),
              'output_file_md5': calculate_md5(output_file),
              }

    return {full_path_name: struct} if full_path_name else struct
