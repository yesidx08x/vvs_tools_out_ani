import os
import glob
import pymel.core as pm

class SequenceIdentifier:
    def __init__(self, filepath):
        self.filepath = filepath
        self.name_pattern = re.compile(r"^(.*?)(\d+)(\..+)$")
        self.start_frame = None
        self.end_frame = None
        self.padding = None
        self.format = None
        self.frame_range = []
        if self.filepath:
            self._analyze_sequence()

    def _analyze_sequence(self):

        dirname, basename = os.path.split(self.filepath)
        match = self.name_pattern.match(basename)
        if not match:
            raise ValueError("The file name format does not match a recognized sequence pattern.")

        name, frame_str, ext = match.groups()
        frame_len = len(frame_str)
        prefix = name
        suffix = ext
        self.format = format_path_join(dirname, "{}{}{}".format(prefix, '#' * frame_len, suffix))

        files = os.listdir(dirname)
        sequence_files = []
        for file in files:
            file_match = self.name_pattern.match(file)
            if file_match:
                file_name, file_frame_str, file_ext = file_match.groups()
                if file_name == prefix and file_ext == suffix and len(file_frame_str) == frame_len:
                    sequence_files.append(int(file_frame_str))

        if not sequence_files:
            raise ValueError("No matching sequence files found.")

        sequence_files.sort()
        self.start_frame = sequence_files[0]
        self.end_frame = sequence_files[-1]
        self.padding = frame_len
        self.frame_range = sequence_files

    def get_start_frame(self):
        return self.start_frame

    def get_end_frame(self):
        return self.end_frame

    def get_frame_range(self):
        return self.frame_range

    def get_padding_num(self):
        return self.padding

    def get_format(self):
        return self.format


def main():
    search_path = r'R:\1031_XHRM\VFX\Sequences\test\0260\CG\Efx\Work\ZTH\00_tolighting\v004\*_seq'
    folders = [folder for folder in glob.glob(search_path) if os.path.isdir(folder)]
    for folder in folders:
        abc=glob.glob(os.path.join(folder, '*.abc'))
        first_frame_abc=abc[0]
        node_name=folder.split('\\')[-1].split('/')[-1]
        node_shape = pm.createNode('aiStandIn', name=node_name + '_aiStandInShape')
        node_shape.getParent().rename(node_name + '#')
        node_shape.attr('dso').set(first_frame_abc)
        node_shape.attr('useFrameExtension').set(1)


