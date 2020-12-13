# coding=utf-8
import os

from .executor import IExecutor
from ..header_def import HeaderInferred, HeaderDef, OutputType
from ..readers.csv_reader import CSVReader
from ..writers.default_dict_writer import DefaultDictWriter

if False:
    from typing import Dict


class TableExporter(IExecutor):
    def __init__(self):
        self.table_data = {}

    def execute(self, def_module):
        reader = CSVReader()
        head_inferred = getattr(def_module, 'head_inferred', HeaderInferred())
        headers = def_module.headers  # type: Dict[str, HeaderDef]
        inputs = def_module.input_files
        table_data = reader.read(head_inferred, headers, inputs)

        default_data = HeaderDef.make_default_data(headers.values())
        indexes = getattr(def_module, 'indexes', [])
        output_type = def_module.output_type
        output_name = def_module.output_name
        header_map = HeaderDef.make_header_map(headers.values())
        for single_type, dir_name in OutputType.get_dirs(output_type):
            single_data = self.redirect_table_data(single_type, header_map, table_data)
            single_default_data = self.redirect_default_data(single_type, header_map, default_data)
            single_index = self.redirect_indexes(single_type, header_map, indexes)
            if single_type & OutputType.CLIENT:
                limit = getattr(def_module, 'num_limit', 100)
            else:
                limit = -1
            writer = DefaultDictWriter(single_data, single_default_data, single_index, limit)
            package_path = os.path.join(dir_name, output_name)
            writer.write_to(package_path)

    @classmethod
    def redirect_table_data(cls, output_type, header_map, table_data):
        # type: (int, Dict[str, HeaderDef], dict) -> dict
        data = {}
        for key, value in table_data.iteritems():
            new_value = {}
            for name, header in header_map.iteritems():
                if header.output & output_type == 0:
                    continue
                if header.primary_key and not header.primary_key.retain:
                    continue
                new_value[name] = value[name]
            data[key] = new_value
        return data

    @classmethod
    def redirect_default_data(cls, output_type, header_map, default_data):
        # type: (int, Dict[str, HeaderDef], dict) -> dict
        data = {}
        for key, value in default_data.iteritems():
            header = header_map[key]
            if header.output & output_type == 0:
                continue
            data[key] = value
        return data

    @classmethod
    def redirect_indexes(cls, output_type, header_map, indexes):
        # type: (int, Dict[str, HeaderDef], list) -> list
        data = []
        for index_name in indexes:
            if header_map[index_name].output & output_type:
                data.append(index_name)
        return data
