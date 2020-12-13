# coding=utf-8
from utils import time_utility
if False:
    from typing import Any


class ConvertError(Exception):
    pass


class DataType(object):
    __slots__ = ()

    hashable = property(lambda self: False)

    def check_def_valid(self):
        used_chars = []
        for char in self.get_special_chars():
            if char in used_chars:
                raise Exception('%s 定义不合法' % self.get_type_desc())
            used_chars.append(char)

    def convert(self, input_data):
        try:
            return self.convert_imp(input_data)
        except ValueError:
            msg = "\"%s\"不是有效的数据类型：%s" % (input_data, self.get_type_desc())
            raise ConvertError(msg)

    def convert_imp(self, input_data):  # type: (str) -> Any
        raise NotImplementedError

    def get_type_desc(self):
        raise NotImplementedError

    def get_default(self):
        raise NotImplementedError

    def get_special_chars(self):
        return []


class Str(DataType):
    def convert_imp(self, input_data):  # type: (str) -> Any
        return str(input_data)

    def get_type_desc(self):
        return 'Str'

    def get_default(self):
        return ""


class Bool(DataType):
    def convert_imp(self, input_data):  # type: (str) -> Any
        return bool(eval(input_data))

    def get_type_desc(self):
        return 'Bool'

    def get_default(self):
        return False


class Int(DataType):
    __slots__ = 'base',

    hashable = property(lambda self: True)

    def __init__(self, base=10):
        self.base = base

    def convert_imp(self, input_data):
        return int(input_data, self.base)

    def get_type_desc(self):
        return 'Int[base:%s]' % self.base

    def get_default(self):
        return 0


class Float(DataType):
    __slots__ = 'ndigits',

    hashable = property(lambda self: True)

    def __init__(self, ndigits=None):
        self.ndigits = ndigits

    def convert_imp(self, input_data):
        return round(float(input_data), self.ndigits)

    def get_type_desc(self):
        return 'Float'

    def get_default(self):
        return 0.0


class List(DataType):
    __slots__ = 'elem_type', 'sep'

    hashable = property(lambda self: False)

    def __init__(self, elem_type, sep=','):
        # type: (DataType, str) -> None
        self.elem_type = elem_type
        self.sep = sep
        self.check_def_valid()

    def convert_imp(self, input_data):  # type: (str) -> Any
        return [self.elem_type.convert(elem_str) for elem_str in input_data.split(self.sep)]

    def get_type_desc(self):
        elem_desc = self.elem_type.get_type_desc()
        fmt_str = '%s%s...' % (elem_desc, self.sep)
        return '%s[%s]' % (self.__class__.__name__, fmt_str)

    def get_default(self):
        return []

    def get_special_chars(self):
        return list(self.sep) + self.elem_type.get_special_chars()


class Tuple(List):
    __slots__ = ()

    hashable = property(lambda self: True)

    def convert_imp(self, input_data):  # type: (str) -> Any
        return tuple(super(Tuple, self).convert_imp(input_data))

    def get_default(self):
        return ()


class Dict(DataType):
    __slots__ = 'key_type', 'value_type', 'sep', 'kv_sep'

    hashable = property(lambda self: False)

    def __init__(self, key_type, value_type, sep, kv_sep):
        # type: (DataType, DataType, str, str) -> None
        self.key_type = key_type
        self.value_type = value_type
        self.sep = sep
        self.kv_sep = kv_sep
        assert self.key_type.hashable, '%s 不能作为Dict的Key类型' % key_type.get_type_desc()
        self.check_def_valid()

    def convert_imp(self, input_data):
        data = {}
        for kv_str in input_data.split(self.sep):
            kv_seq = kv_str.split(self.kv_sep)
            if len(kv_seq) != 2:
                raise ConvertError("[\"%s\"]不是有效的Dict元素值[%s]" % (kv_str, self.get_kv_fmt()))
            key = self.key_type.convert(kv_seq[0])
            if key in data:
                raise ConvertError("Dict中存在重复的Key")
            data[key] = self.value_type.convert(kv_seq[1])
        return data

    def get_kv_fmt(self):
        key_desc = self.key_type.get_type_desc()
        value_desc = self.value_type.get_type_desc()
        return '%s%s%s' % (key_desc, self.kv_sep, value_desc)

    def get_type_desc(self):
        kv_fmt = self.get_kv_fmt()
        return 'Dict[%s%s...]' % (kv_fmt, self.sep)

    def get_special_chars(self):
        return self.key_type.get_special_chars() + self.value_type.get_special_chars()

    def get_default(self):
        return {}


class Timestamp(DataType):

    __slots__ = 'fmt'

    def __init__(self, fmt):
        self.fmt = fmt
        self._fmt_test()

    def _fmt_test(self):
        time_utility.timestamp2date_str(0, self.fmt)

    def convert_imp(self, input_data):
        return time_utility.date_str2timestamp(input_data, self.fmt)

    def get_type_desc(self):
        return 'Timestamp[%s]' % self.fmt

    def get_default(self):
        return 0
