from log.singleton import Singleton
import logging
import sys

ERROR = logging.ERROR
WARNING = logging.WARNING
INFO = logging.INFO
DEBUG = logging.DEBUG


class Logger(Singleton):
    __logger = None

    def __init__(self):
        formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        handler = logging.FileHandler('log.txt', mode='w')
        handler.setFormatter(formatter)
        screen_handler = logging.StreamHandler(stream=sys.stdout)
        screen_handler.setFormatter(formatter)
        logger = logging.getLogger('logger')
        logger.setLevel(DEBUG)
        logger.addHandler(handler)
        logger.addHandler(screen_handler)
        self.__logger = logger

    def set_log_level(self, level: int):
        self.__logger.setLevel(level)

    def debug(self, message):
        self.__logger.debug(message)

    def info(self, message):
        self.__logger.info(message)

    def warning(self, message):
        self.__logger.warning(message)

    def error(self, message):
        self.__logger.error(message)
