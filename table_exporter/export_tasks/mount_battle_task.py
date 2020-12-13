# coding=utf-8
from exporter.data_type import *
from exporter.header_def import *
from exporter.executors.table_exporter import TableExporter
from .test_dir import test_data_task


# header_inferred = HeaderInferred()

def icon_hooker(icon):
    return '%s.png' % icon


headers = {
    '段位': HeaderDef('lv1', Int(), required=True, primary_key=PrimaryKey(0)),
    '小段位': HeaderDef('lv2', Int(), required=True, primary_key=PrimaryKey(1, True)),
    '是否为排名段位': HeaderDef('is_sort', Bool()),
    '段位名称': HeaderDef('name', Str(), output=OutputType.CLIENT),
    '段位图标': HeaderDef('icon', Str(), data_hooker=icon_hooker, output=OutputType.CLIENT),
    '分段升星': HeaderDef('seq_level', Tuple(Int()))
}

input_files = [
    "妖灵弈段位表",
]

output_name = "mount_battle_data"
output_type = OutputType.COMMON
dependencies = [test_data_task]
num_limit = 10
indexes = ['lv2']


class _Exporter(TableExporter):

    @classmethod
    def redirect_table_data(cls, output_type, header_map, table_data):
        # type: (int, Dict[str, HeaderDef], dict) -> dict
        data = super(_Exporter, cls).redirect_table_data(output_type, header_map, table_data)
        return data


executor = _Exporter()
