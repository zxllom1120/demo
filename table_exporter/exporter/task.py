# coding=utf-8
from utils import config
from utils.event import Event
from utils.log_manager import LogManager
import fingerprint
if False:
    from typing import Set


class Task(object):
    def __init__(self, def_module):
        self.def_module = def_module
        self.dependencies = set()  # type: Set[Task]
        self.fingerprint = ""
        self.reexported = False
        self.dependency_reexported = False
        self.finish_event = Event()

        index = self.task_name.find('.')
        self.short_name = self.task_name[index + 1:]
        self.logger = LogManager.get_logger('Task')

    task_name = property(lambda self: self.def_module.__name__)

    def __str__(self):
        return "<Task: %s>" % self.short_name

    def init(self):
        from utils import methods
        for name, header in self.def_module.headers.iteritems():
            header.set_design_name(name)
        filenames = ['input_data/%s.csv' % filename for filename in self.def_module.input_files]
        self.fingerprint = methods.calc_files_md5(self.def_module.__file__, *filenames)

    def add_dependency(self, dependency):  # type: (Task) -> None
        self.dependencies.add(dependency)
        dependency.finish_event += self.on_dependency_finish

    def on_dependency_finish(self, dependency):  # type: (Task) -> None
        if dependency.reexported:
            self.dependency_reexported = True
        self.dependencies.discard(dependency)

    def can_execute(self):
        return len(self.dependencies) == 0

    def execute(self):
        if not self._need_export():
            self.on_export_finish()
            return True
        self.reexported = True
        self.def_module.executor.execute(self.def_module)
        self.on_export_finish()
        return True

    def _need_export(self):
        old_fingerprint = fingerprint.data.get(self.short_name)
        if not old_fingerprint:
            return True
        if old_fingerprint != self.fingerprint:
            return True
        if self.dependency_reexported:
            return True
        return False

    def on_export_finish(self):
        self.finish_event(self)
        fingerprint.data[self.short_name] = self.fingerprint
        self.logger.info('%s task done, reexported: %s', self.short_name, self.reexported)
