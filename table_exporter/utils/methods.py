# coding=utf-8
import os


def calc_files_md5(*filenames):
    import hashlib
    md5 = hashlib.new('md5')
    for filename in sorted(filenames):
        with open(filename) as f:
            while True:
                chunk = f.read(1 << 16)
                if not chunk:
                    break
                md5.update(chunk)
    return md5.hexdigest()


def make_package(path):

    def try_gen_init():
        init_path = os.path.join(path, '__init__.py')
        if os.path.exists(init_path):
            return
        f = open(init_path, 'w')
        f.close()

    if os.path.isdir(path):
        try_gen_init()
        return

    assert not os.path.exists(path)
    make_package(os.path.dirname(path))
    os.mkdir(path)
    try_gen_init()


def save_fingerprint():
    import fingerprint
    from py_dumper import dump
    dump(fingerprint.data, 'fingerprint.py', use_taggeddict=False, reload_all=False)
