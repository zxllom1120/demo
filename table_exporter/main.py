# coding=utf-8
import os
import argparse


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear-all', action='store_true', default=False)
    return parser


def clear_all():
    import shutil
    if os.path.exists('output_data'):
        shutil.rmtree('output_data')

    import fingerprint
    fingerprint.data.clear()


def ensure_output_package():
    from utils import methods
    from exporter.header_def import OutputType

    for _, dir_name in OutputType.get_dirs(OutputType.ALL):
        path = os.path.abspath(dir_name)
        methods.make_package(path)


def main():
    import sys
    from utils import methods
    from exporter.task_graph import TaskGroup
    parser = get_parser()
    args = parser.parse_args(sys.argv[1:])

    if args.clear_all:
        clear_all()
    ensure_output_package()

    graph = TaskGroup()
    graph.init()
    graph.run()
    methods.save_fingerprint()


if __name__ == '__main__':
    main()
