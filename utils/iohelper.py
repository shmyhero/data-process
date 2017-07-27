import os
import glob


def ensure_dir_exists(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def ensure_parent_dir_exists(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)


def read_file_to_string(file_path):
    f = open(file_path, 'r')
    content = f.read()
    f.close()
    return content


def write_to_file(file_path, content):
    f = open(file_path, 'w')
    f.write(content)
    f.close()


def get_sub_dir_names(path):
    if os.path.exists(path):
        file_names = os.listdir(path)
        for file_name in file_names:
            file_path = os.path.join(path, file_name)
            if os.path.isdir(file_path):
                yield file_name


def get_sub_files(path, ext = None):
    sub_path = '*.' + ext if ext else '*'
    str_path = os.path.join(path, sub_path)
    return glob.glob(str_path)


if __name__ == '__main__':
    print list(get_sub_dir_names('/Users/tradehero/quicklisp'))