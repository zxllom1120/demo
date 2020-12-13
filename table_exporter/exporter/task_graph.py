# coding=utf-8
import os
import sys
from .task import Task
from utils.log_manager import LogManager
if False:
    from typing import List


class TaskGroup(object):

    def __init__(self):
        self.tasks = []  # type: List[Task]
        self.logger = LogManager.get_logger('TaskGroup')

    def init(self):
        for top, dirs, nondirs in os.walk('export_tasks'):
            package = top.replace('\\', '/').replace('/', '.')
            for name in nondirs:
                module_name, ext = os.path.splitext(name)
                if module_name == '__init__' or ext != '.py':
                    continue
                path = '%s.%s' % (package, module_name)
                __import__(path)
                module = sys.modules[path]
                if getattr(module, 'DEACTIVATED', False):
                    continue
                task = Task(sys.modules[path])
                task.init()
                self.tasks.append(task)
        self.connect_dependency()

    def connect_dependency(self):
        task_map = {task.task_name: task for task in self.tasks}
        for task in self.tasks:
            for module in getattr(task.def_module, 'dependencies', []):
                if getattr(module, 'DEACTIVATED', False):
                    raise Exception('依赖文件：%s 未激活' % module.__name__)
                task.add_dependency(task_map[module.__name__])

    def run(self):
        while self.tasks:
            for task in self.tasks[:]:
                if not task.can_execute():
                    continue
                task.execute()
                self.tasks.remove(task)
        self.logger.info('all task done')
