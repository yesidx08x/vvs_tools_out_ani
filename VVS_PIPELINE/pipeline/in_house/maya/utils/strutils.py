# -*-coding:utf-8-*-
import os

def format_path(path):
    return os.path.normpath(path).replace('\\', '/').replace('\t', '/t').replace('\n', '/n').replace('\a', '/a')


def format_path_join(path, *paths):
    return format_path(os.path.join(path, *paths))


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(min(len(size_name) - 1, (size_bytes.bit_length() - 1) // 10))
    p = 1 << (i * 10)
    size = round(size_bytes / p, 3)
    return "{} {}".format(size, size_name[i])

def get_file_size(file_path):
    try:
        file_size = os.path.getsize(file_path)
        return convert_size(file_size)
    except OSError as e:
        print(u"获取文件大小时出错: {}".format(e))
        return None

if __name__ == '__main__':
    file_size = get_file_size(r'C:\Users\wangfuli.VVS-BEIJING\Desktop\SGZ_S06_0060_lgt_v0009_zhaoyun.ma')
    print(file_size)