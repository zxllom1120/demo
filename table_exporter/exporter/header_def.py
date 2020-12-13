# coding=utf-8
from .data_type import DataType, ConvertError
if False:
    from typing import Optional, Callable, Any, Dict, List
    DATA_HOOKER = Optional[Callable[[Any], Any]]


class OutputType(object):
    CLIENT_ONLY = 1 << 0  # 输出到data.client(client)
    SERVER_ONLY = 1 << 1  # 输出到data.server(server)

    CLIENT_COMMON = 1 << 2  # 输出到data.common(client)
    SERVER_COMMON = 1 << 3  # 输出到data.common(client)

    CLIENT = CLIENT_ONLY | CLIENT_COMMON
    SERVER = SERVER_ONLY | SERVER_COMMON
    COMMON = CLIENT_COMMON | SERVER_COMMON
    ALL = CLIENT | SERVER | COMMON

    @classmethod
    def get_dirs(cls, output_type):
        dirs = []
        if output_type & cls.CLIENT_ONLY:
            dirs.append((cls.CLIENT_ONLY, 'output_data/client_data'))
        if output_type & cls.SERVER_ONLY:
            dirs.append((cls.SERVER_ONLY, 'output_data/server_data'))
        if output_type & cls.CLIENT_COMMON:
            dirs.append((cls.CLIENT_COMMON, 'output_data/client_common'))
        if output_type & cls.SERVER_COMMON:
            dirs.append((cls.SERVER_COMMON, 'output_data/server_common'))
        return dirs


class ForeignKey(object):
    def __init__(self, data_path):
        self.data_path = data_path


class PrimaryKey(object):
    def __init__(self, index=0, retain=False):
        self.index = index
        # 主键的数据最终是否保留在data内
        self.retain = retain


class HeaderDef(object):
    __slots__ = 'name', 'data_type', 'required', 'output', 'primary_key', 'foreign_key', \
                'data_hooker', 'default', 'design_name'

    def __init__(
            self,
            name,
            data_type,
            required=False,
            output=OutputType.COMMON,
            primary_key=None,
            foreign_key=None,
            data_hooker=None,
            default=None,
    ):
        # type: (str, DataType, bool, int, Optional[PrimaryKey], Optional[ForeignKey], DATA_HOOKER, Any) -> None

        self.design_name = ""
        self.name = name
        self.data_type = data_type      # type: DataType
        # 是否不可缺少
        self.required = required        # type: bool
        # 哪些输出目录需要这列数据
        self.output = output            # type: int
        # 主键
        self.primary_key = primary_key  # type: Optional[PrimaryKey]
        # 外建
        self.foreign_key = foreign_key  # type: Optional[ForeignKey]
        # 数据后处理函数
        self.data_hooker = data_hooker  # type: DATA_HOOKER
        # 默认值
        self.default = default
        # 如果作为主键，则强制双端输出
        if self.primary_key:
            self.output = OutputType.COMMON

    def set_design_name(self, design_name):
        self.design_name = design_name

    def convert(self, input_data):
        if not input_data and self.required:
            raise ConvertError('%s数据不可为空' % self.design_name)
        data = self.data_type.convert(input_data) if input_data else self.get_default()
        if self.data_hooker:
            data = self.data_hooker(data)
        return data

    def get_default(self):
        import copy
        if self.default is not None:
            return copy.deepcopy(self.default)
        return self.data_type.get_default()

    @classmethod
    def make_header_map(cls, headers):  # type: (List[HeaderDef]) -> Dict
        header_map = {}
        for header in headers:
            header_map[header.name] = header
        return header_map

    @classmethod
    def make_default_data(cls, headers):  # type: (List[HeaderDef]) -> dict
        default_data = {}
        for header in headers:
            if header.primary_key:
                continue
            default_data[header.name] = header.get_default()
        return default_data


class HeaderType(object):
    ROW = 1
    COL = 2


class HeaderInferred(object):
    """
    指定表头所在位置，第几行/第几列
    """

    def __init__(self, header_type=HeaderType.ROW, line=1):
        self.header_type = header_type
        self.line = line
