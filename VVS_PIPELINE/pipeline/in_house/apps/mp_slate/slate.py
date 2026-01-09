import os
import json
import tempfile
import argparse
import nuke

template_file = 'L:/VVS_PIPELINE/vvs-dcc-plugins/nuke/proj_{project}/gizmo/mp.nk'.format(
    project=os.getenv('project_name'))

parser = argparse.ArgumentParser()
parser.add_argument("json_path", type=str, help="json file path")
args = parser.parse_args()

with open(args.json_path, 'r', encoding='utf-8') as f:
    _data = json.load(f)

project_name = os.getenv('project_name')
OCIO = os.getenv('OCIO').replace('\\', '/')

input_files = _data.get('input_files')

print(OCIO)


def format_path(path):
    return os.path.normpath(path).replace('\\', '/').replace('\t', '/t').replace('\n', '/n').replace('\a', '/a')


def format_path_join(path, *paths):
    return format_path(os.path.join(path, *paths))


def __save_temp_nk(file_name):
    temp_dir = tempfile.mkdtemp()
    path = format_path_join(temp_dir, "{}.nk".format(file_name))
    nuke.scriptSaveAs(path)


def create_ocio():
    ocio_config_path = OCIO
    if not os.path.exists(ocio_config_path):
        return False

    ocio_config = {
        "colorManagement": "OCIO",
        "OCIO_config": "custom",
        "customOCIOConfigPath": ocio_config_path,
        "monitorOutLUT": "Rec.709 (ACES)",
        "monitorLut": "Rec.709 (ACES)"

    }
    for attr, value in ocio_config.items():
        nuke.root()[attr].setValue(value)
        nuke.knobDefault(attr, value)
    return True


exitcode = 0

create_ocio()
nuke.scriptReadFile(template_file)

read = [node for node in nuke.allNodes() if node.Class() == "Read"][0]
write = [node for node in nuke.allNodes() if node.Class() == "Write"][0]
slate = [node for node in nuke.allNodes() if node.Class() == "Group"][0]

for k, v in _data.items():
    if k == 'config':
        continue
    input_file = _data[k]['input_file']
    output_file = _data[k]['output_file']
    shot_info = _data[k]['shot_info']

    read["file"].setValue(input_file)
    slate['message'].setValue(shot_info)
    write['file'].setValue(output_file)

    if write:
        try:
            nuke.executeMultiple([write], ([1, 1, 1],), [nuke.views()[0]])
            print('\n[FINISH][%s]' % k)
        except:
            pass
print('\n[SUCCESS]')
__save_temp_nk('mp_slate')

exit(exitcode)
