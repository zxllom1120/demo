# coding=utf-8
import os
import shutil

from utils.py_dumper import dump, DumpType
from utils import methods


def _ensure_path(path):
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    methods.make_package(path)


class DefaultDictWriter(object):

    def __init__(self, table_data, default_data, indexes, num_limit=-1):
        # type: (dict, dict, list, int) -> None
        self.table_data = table_data
        self.default_data = default_data
        self.indexes = indexes
        self._module2keys = {}
        self.num_limit = num_limit if num_limit > 0 else len(self.table_data)

    def write_to(self, path):
        _ensure_path(path)
        self._make_init(path)
        self._make_data_files(path)
        self._make_config(path)
        self._make_indexes(path)

    def _make_init(self, path):
        init_content = """# coding=utf-8
from helper.common.table_data import TableData
from . import config

data = TableData(config)
_reload_all = True
"""
        with open(os.path.join(path, '__init__.py'), 'w') as f:
            f.write(init_content)

    def _make_data_files(self, path):
        keys = sorted(self.table_data)
        idx = 1
        while True:
            data = {}
            for key in keys[(idx - 1) * self.num_limit: idx * self.num_limit]:
                data[key] = self.table_data[key]
            if not data:
                break
            self._module2keys[idx] = sorted(data.keys())
            file_path = os.path.join(path, 'data_%s.py' % idx)
            dump(data, file_path, record_time=True, one_line=True)
            idx += 1

    def _make_config(self, path):
        data = {
            'default_data': self.default_data,
            'module2keys': self._module2keys,
        }
        dump(
            data, os.path.join(path, 'config.py'),
            dump_type=DumpType.FIRST_KEYS_AS_ATTR,
            recode_time=True,
            one_line=True,
        )

    def _make_indexes(self, path):
        for index_name in self.indexes:
            data = {}
            for key, value in self.table_data.iteritems():
                try:
                    index_data = value[index_name]
                except KeyError:
                    index_data = self.default_data[index_name]
                data.setdefault(index_data, []).append(key)
            for key in data:
                data[key] = sorted(data[key])
            filename = os.path.join(path, 'index_%s.py' % index_name)
            dump(data, filename, record_time=True, one_line=True)
