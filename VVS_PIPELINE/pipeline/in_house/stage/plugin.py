
import os
import sys
import inspect
import logging
import types
from stage.external import six
from stage import  _registered_plugins
log = logging.getLogger("stage.plugin")


def _imported_module(pipeline_name,abspath):
    mod_name = f"stage.{pipeline_name}"

    module = types.ModuleType(mod_name)
    module.__file__ = abspath

    try:
        with open(abspath, "rb") as f:
            six.exec_(f.read(), module.__dict__)
        sys.modules[abspath] = module

    except Exception as err:
        log.error("Skipped: \"%s\" (%s)", mod_name, err)
        return

    return module

def plugins_from_module(module):
    for name in dir(module):

        if name.startswith("_"):
            continue

        cls = getattr(module, name)

        if not inspect.isclass(cls):
            continue

        if 'AddonCore' == cls.__name__:
            continue
        if 'AppCore' == cls.__name__:
            continue
        if 'Path' == cls.__name__:
            continue

        return cls

def register_plugin(plugin):

    _registered_plugins[plugin.__name__] = plugin

def  addon_initialize(pipeline_name):
    addons_path = os.path.join(os.path.dirname(__file__), 'addons')
    addons = [d for d in os.listdir(addons_path) if d == pipeline_name]
    if not addons:
        raise ImportError("No pipeline {} found in addons folder".format(pipeline_name))
    module_path = os.path.join(addons_path, addons[0], 'addon.py')

    return plugins_from_module(_imported_module(pipeline_name, module_path))

def  app_initialize(app_name):
    addons_path = os.path.join(os.path.dirname(__file__), 'apps')
    addons = [d for d in os.listdir(addons_path) if d == app_name]
    if not addons:
        raise ImportError("No app {} found in addons folder".format(app_name))
    module_path = os.path.join(addons_path, addons[0], 'app.py')
    os.environ["STAGE_DCC"] = app_name
    return plugins_from_module(_imported_module(app_name, module_path))

def  project_initialize(project_name):
    project_config_path = os.path.join(os.path.dirname(__file__), 'config','project')

    addons = [d for d in os.listdir(project_config_path) if d.split('.')[0] == project_name]
    if not addons:
        module_path = os.path.join(project_config_path, 'default','settings.py')
    else:
        module_path = os.path.join(project_config_path, addons[0],'settings.py')

    obj=plugins_from_module(_imported_module(project_name, module_path))
    return obj