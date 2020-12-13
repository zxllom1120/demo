# coding=utf-8
import os
import csv
from ..header_def import HeaderDef, HeaderInferred, HeaderType
from ..data_type import ConvertError
if False:
    from typing import Dict, List, Tuple


class CSVReader(object):

    @classmethod
    def read(cls, head_inferred, headers, inputs):
        # type: (HeaderInferred, Dict[str, HeaderDef], List[str]) -> Dict
        result = {}
        primary_keys = cls.gen_primary_key(headers)
        assert primary_keys
        for filename in inputs:
            data_list, header_data = cls.read_file(head_inferred, filename)
            header_map = {}
            for name, header_def in headers.iteritems():
                assert name in header_data
                index = header_data.index(name)
                header_map[index] = header_def
            for data in data_list:
                ret = {}
                for index, header_def in header_map.iteritems():
                    data_str = data[index] if index < len(data) else ""
                    try:
                        ret[header_def.name] = header_def.convert(data_str)
                    except ConvertError, e:
                        name = os.path.basename(filename)
                        line = data_list.index(data) + head_inferred.line + 3
                        raise ConvertError("%s第%d行数据出错, %s" % (name, line, e))
                keys = tuple(ret[name] for name in primary_keys)
                key = keys[0] if len(keys) == 1 else keys
                if key in result:
                    raise ConvertError('发现存在重复的Key: %s, 输入数据: %s' % (key, ", ".join(inputs)))
                result[key] = ret
        return result

    @classmethod
    def gen_primary_key(cls, headers):  # type: (Dict[str, HeaderDef]) -> tuple
        primary_headers = []
        primary_indexes = []
        for header in headers.itervalues():
            if header.primary_key:
                assert header.primary_key.index not in primary_indexes
                primary_headers.append(header)
                primary_indexes.append(header.primary_key.index)
        primary_headers.sort(key=lambda obj: obj.primary_key.index)
        return tuple(header.name for header in primary_headers)

    @classmethod
    def read_file(cls, head_inferred, filename):
        # type: (HeaderInferred, str) -> Tuple[List[List], List]
        rows = []
        for row in csv.reader(file('input_data/%s.csv' % filename)):
            row = [elem.decode('GB2312').encode('utf-8') for elem in row]
            rows.append(row)
        if head_inferred.header_type == HeaderType.ROW:
            data = [row for row in rows[head_inferred.line + 2:] if row and row[0] in ("是", )]
        else:
            data = []
        header_data = rows[head_inferred.line]
        return data, header_data
