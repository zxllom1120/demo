# coding=utf-8
import sys


class _Data(dict):
    __slots__ = '_data', '_default'

    def __init__(self, data, default):
        super(_Data, self).__init__(data)
        self._default = default

    def __getitem__(self, key):
        try:
            return super(_Data, self).__getitem__(key)
        except KeyError:
            return self._default[key]

    def get(self, key, default=None):
        raise Exception('use [] instead')


class TableData(object):
    __slots__ = '_config', '_data', '_indexes', '_data_package', '_unload_modules'

    def __init__(self, config):
        self._data = {}
        self._indexes = {}
        self._config = config
        self._unload_modules = dict(self._config.module2keys)
        self._data_package = config.__package__

    def __getitem__(self, key):
        try:
            return _Data(self._data[key], self._config.default_data)
        except KeyError:
            self._load_data_by_key(key)
            return _Data(self._data[key], self._config.default_data)

    def __setitem__(self, key, value):
        self._data[key] = value

    def __contains__(self, key):
        try:
            self[key]
            return True
        except KeyError:
            return False

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def get_by_index(self, key, index_name):
        try:
            index_data = self._indexes[index_name]
        except KeyError:
            module_path = '%s.index_%s' % (self._data_package, index_name)
            __import__(module_path)
            index_data = self._indexes[index_name] = sys.modules[module_path].data
        try:
            return index_data[key]
        except KeyError:
            return ()

    def items(self):
        return [item for item in self.iteritems()]

    def keys(self):
        return [key for key in self.iterkeys()]

    def values(self):
        return [value for value in self.itervalues()]

    def iteritems(self):
        for key in self:
            yield key, self[key]

    def __iter__(self):
        for key in self._data:
            yield key

        for keys in self._unload_modules.values():
            for key in keys:
                yield key

    def iterkeys(self):
        return self.__iter__()

    def itervalues(self):
        for key in self:
            yield self[key]

    def reset(self):
        self._data = {}
        self._indexes = {}
        self._unload_modules = dict(self._config.module2keys)

    def _load_data_by_key(self, key):
        module = self._load_module_by_key(key)
        if not module:
            raise KeyError(key)
        self._data.update(module.data)

    def _load_module_by_key(self, key):
        for index, keys in self._unload_modules.iteritems():
            if key not in keys:
                continue
            self._unload_modules.pop(index)
            module_path = '%s.data_%s' % (self._data_package, index)
            __import__(module_path)
            print 'load', module_path
            return sys.modules[module_path]
