
from functools import wraps
import re
from maya import cmds
from maya import mel



def get_ranges():
    r_ast = cmds.playbackOptions(query=True, animationStartTime=True)
    r_min = cmds.playbackOptions(query=True, minTime=True)
    r_max = cmds.playbackOptions(query=True, maxTime=True)
    r_aet = cmds.playbackOptions(query=True, animationEndTime=True)
    return [r_ast, r_min, r_max, r_aet]


def set_ranges(range_list):
    cmds.playbackOptions(
        animationStartTime=range_list[0],
        minTime=range_list[1],
        maxTime=range_list[2],
        animationEndTime=range_list[3],
    )


def get_scene_fps():
    """Return the current FPS value set by DCC. None if not supported."""
    return mel.eval("currentTimeUnitToFPS")


def set_scene_fps(fps_value):

    if int(fps_value) == fps_value:
        fps_value = int(fps_value)
    try:
        mel.eval(f"currentUnit -time {fps_value}fps;")
    except RuntimeError as exc:
        raise RuntimeError("Invalid FPS value") from exc


def keepselection(func):

    @wraps(func)
    def _keepfunc(*args, **kwargs):
        original_selection = cmds.ls(selection=True)
        component_state = cmds.selectMode(query=True, component=True)
        object_state = cmds.selectMode(query=True, object=True)
        try:
            # start an undo chunk
            return func(*args, **kwargs)
        except Exception as exc:
            raise exc
        finally:
            # after calling the func, end the undo chunk and undo
            cmds.selectMode(object=object_state, component=component_state)
            cmds.select(original_selection)

    return _keepfunc

def ls_regex(val):
    res = []
    reg=re.compile(r'(\||^)' + val)
    transforms=cmds.ls(type='transform')
    for transform in transforms:
        if reg.search(transform,re.IGNORECASE):
            res.append(transform)
    return res


