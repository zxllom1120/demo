# coding=utf-8
from abc import ABCMeta, abstractmethod


class IExecutor(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute(self, **kwargs):
        pass
