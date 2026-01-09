import os
import re
import json
import hashlib
import platform
from datetime import datetime
CURRENT_PLATFORM = platform.system()

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

def get_home_dir():

    if CURRENT_PLATFORM == "Windows":
        return os.path.normpath(os.getenv("USERPROFILE"))
    return os.path.normpath(os.getenv("HOME"))

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def sanitize(name):
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
    return re.sub(invalid_chars, '-', name)

def calculate_md5(file_path, chunk_size=8192):
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            md5.update(chunk)
    return md5.hexdigest()

def save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)