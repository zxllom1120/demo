# coding=utf-8
from exporter.data_type import *
from exporter.header_def import *
from exporter.executors.table_exporter import TableExporter
# from .. import mount_battle_task

# 不激活导表
# DEACTIVATED = True

header_inferred = HeaderInferred()

headers = {
    '表头1': HeaderDef('header1', Int(), required=True, primary_key=PrimaryKey()),
    '表头2': HeaderDef('header2', Int()),
}

input_files = [
]

output_name = "test_data"
output_type = OutputType.CLIENT_ONLY
dependencies = []

executor = TableExporter()
