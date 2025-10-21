from src.modules.logger_implemenation.logger_macros import *
from inspect import FrameInfo
from datetime import datetime
from colorama import Fore, Style
import os


class LogData:
    payload: str
    level: str
    timestamp: datetime
    frame: FrameInfo

    def __init__(self, payload: str, frame: FrameInfo, level: str = DEFAULT_LEVEL, timestamp: datetime = None):
        self.payload = payload
        self.frame = frame
        self.level = level
        self.timestamp = timestamp if type(
            timestamp) is datetime else datetime.now().astimezone()   


def stdout_formatter(data: LogData) -> str:
    fname = os.path.basename(data.frame.filename)
    func = data.frame.function
    lineno = data.frame.lineno
    level = data.level.ljust(LEVELS_MAX_STR_LEN)
    payload = data.payload
    return f"{level} {fname}::{func}::{lineno} {payload}\n"


def logfile_formatter(data: LogData) -> str:
    dt = data.timestamp.isoformat()
    return f"{dt} {stdout_formatter(data)}"