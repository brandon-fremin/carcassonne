# DO NOT REMOVE IMPORTS, they forward to other modules!
from src.modules.logger_implemenation.logger_logwriter import LogWriter, StdoutLogWriter, FileLogWriter, ColorizedLogWriter
from src.modules.logger_implemenation.logger_logdata import LogData
from src.modules.logger_implemenation.logger_class import Logger
from src.modules.logger_implemenation.logger_macros import DEBUG, INFO, WARN, ERROR, FATAL, LEVELS, LEVELS_MAX_STR_LEN
from src.modules.macros import FRAME
from inspect import FrameInfo
from typing import List


GLOBAL_LOGGER = Logger()


def debug(s: str, frame: FrameInfo = None):
    GLOBAL_LOGGER.debug(s, frame if frame else FRAME(1))


def info(s: str, frame: FrameInfo = None):
    GLOBAL_LOGGER.info(s, frame if frame else FRAME(1))


def warn(s: str, frame: FrameInfo = None):
    GLOBAL_LOGGER.warn(s, frame if frame else FRAME(1))


def error(s: str, frame: FrameInfo = None):
    GLOBAL_LOGGER.error(s, frame if frame else FRAME(1))


def fatal(s: str, frame: FrameInfo = None):
    GLOBAL_LOGGER.fatal(s, frame if frame else FRAME(1))


def initialize(logWriters: List[LogWriter] = None):
    GLOBAL_LOGGER.initialize(logWriters)


def attach(logWriter: LogWriter):
    GLOBAL_LOGGER.attach(logWriter)