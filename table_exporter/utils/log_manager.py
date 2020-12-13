# coding=utf-8
import logging


class LogManager(object):
    _loggers = {}

    @classmethod
    def get_logger(cls, name):
        try:
            logger = cls._loggers[name]
        except KeyError:
            logger = cls._loggers[name] = logging.getLogger(name)
            handler = logging.StreamHandler()
            format_list = ['%(asctime)s', '%(filename)s%(lineno)s', '%(name)s', '%(levelname)s', '%(message)s']
            formatter = logging.Formatter(' - '.join(format_list))
            handler.setFormatter(formatter)
            logger.setLevel(logging.DEBUG)
            logger.addHandler(handler)

        return logger
