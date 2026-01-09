import os
import json
import tempfile
import argparse
import nuke

parser = argparse.ArgumentParser()
parser.add_argument("json_path", type=str, help="json file path")
args = parser.parse_args()

with open(args.json_path, 'r', encoding='utf-8') as f:
    _data = json.load(f)


file_types={
    'jpg':'jpeg',
    'tga':'targa',
}



file_scale = eval(_data['config']['file_scale'].replace("x", ''))
data_type = _data['config']['datatype']




OCIO = os.getenv('OCIO').replace('\\', '/')
input_files = _data.get('input_files')

# print(file_type,_data)
print(OCIO)


def format_path(path):
    return os.path.normpath(path).replace('\\', '/').replace('\t', '/t').replace('\n', '/n').replace('\a', '/a')


def format_path_join(path, *paths):
    return format_path(os.path.join(path, *paths))


def __save_temp_nk(file_name):
    temp_dir = tempfile.mkdtemp()
    path = format_path_join(temp_dir, "{}.nk".format(file_name))
    nuke.scriptSaveAs(path)


def __create_output_node():
    node = nuke.createNode("Write")

    # node["ocioColorspace"].setValue("ACES - ACEScg")
    return node


def __create_read_node():
    node = nuke.createNode("Read")


    return node


def __create_format_node():
    r = nuke.createNode("Reformat")
    r['type'].setValue('to box')
    # r['box_width'].setValue(int(width))
    # r['box_height'].setValue(int(height))
    return r


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
read = __create_read_node()

reformat = __create_format_node()
reformat.setInput(0, read)

write = __create_output_node()

write.setInput(0, reformat)

for k, v in _data.items():
    if k == 'config':
        continue
    output_file_type = file_types[_data[k]['output_file_type']] if _data[k]['output_file_type'] in file_types.keys() else  _data[k]['output_file_type']
    input_file_type= _data[k]['input_file_type']

    if input_file_type in ['exr','hdr','dpx','cin']:
        read["raw"].setValue("1")


    input_file = _data[k]['input_file']
    output_file = _data[k]['output_file']

    read["file"].setValue(input_file)

    width = read.width() * file_scale
    height = read.height() * file_scale

    reformat['box_width'].setValue(int(width))
    reformat['box_height'].setValue(int(height))

    write["file_type"].setValue(output_file_type)

    if output_file_type in ['tiff']:
        write["datatype"].setValue(data_type)
        write["colorspace"].setValue("Output - Rec.709")

    if output_file_type in ['exr','hdr','dpx','cin']:
        write["raw"].setValue("1")

    write['file'].setValue(output_file)

    if write:
        try:
            nuke.executeMultiple([write], ([1, 1, 1],), [nuke.views()[0]])
            # nuke.execute(write, 1, 1, 1, [nuke.views()[0]])
            print('\n[FINISH][%s]' % k)
        except:
            pass
print('\n[SUCCESS]')
#__save_temp_nk('exr2tiff')

exit(exitcode)
