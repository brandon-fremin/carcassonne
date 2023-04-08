# DO NOT REMOVE IMPORTS, they forward to other modules!
from src.modules.logger_implemenation.logger_logwriter import LogWriter, StdoutLogWriter, FileLogWriter, ColorizedLogWriter
from src.modules.logger_implemenation.logger_logdata import LogData
from src.modules.logger_implemenation.logger_class import Logger
from src.modules.logger_implemenation.logger_macros import DEBUG, INFO, WARN, ERROR, FATAL, LEVELS, LEVELS_MAX_STR_LEN
from src.modules.macros import FRAME
from inspect import FrameInfo
from typing import List


GLOBAL_LOGGER = Logger()
debug = GLOBAL_LOGGER.debug
info = GLOBAL_LOGGER.info
warn = GLOBAL_LOGGER.warn
error = GLOBAL_LOGGER.error
fatal = GLOBAL_LOGGER.fatal
flush = GLOBAL_LOGGER.flush


def initialize(logWriters: List[LogWriter] = None):
    GLOBAL_LOGGER.initialize(logWriters)


def attach(logWriter: LogWriter):
    GLOBAL_LOGGER.attach(logWriter)