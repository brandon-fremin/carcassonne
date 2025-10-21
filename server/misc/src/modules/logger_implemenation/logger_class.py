from typing import List
from src.modules.logger_implemenation.logger_logwriter \
    import LogWriter, StdoutLogWriter, LogData
from src.modules.logger_implemenation.logger_macros import *
from src.modules.macros import FRAME, FrameInfo
from src.modules.timer import timer_wrapper_factory


class Logger:
    cachedLogs: List[LogData]
    logWriters: List[LogWriter]
    isInitialized: bool

    def __init__(self):
        self.cachedLogs = []
        self.logWriters = []
        self.isInitialized = False

    def __del__(self):
        if not self.isInitialized:
            self.initialize()
        for writer in self.logWriters:
            writer.flush()

    def initialize(self, logWriters: List[LogWriter] = None):
        if self.isInitialized:
            raise Exception("Cannot reinitialize Logger!")
        logWriters = logWriters if logWriters else [StdoutLogWriter()]
        if (not isinstance(logWriters, list)
                or any([not isinstance(lw, LogWriter) for lw in logWriters])
            ):
            raise Exception(f"logWriters must be a list of {type(LogWriter)}!"
                            f" logWriters={logWriters}")

        self.logWriters = logWriters
        for log in self.cachedLogs:
            for writer in self.logWriters:
                writer.write(log)
        self.cachedLogs = []
        self.isInitialized = True
        return self

    def attach(self, logWriter: LogWriter) -> None:
        if not self.isInitialized:
            raise Exception("Cannot attach to un-initialized Logger!")
        if not isinstance(logWriter, LogWriter):
            raise Exception(f"Cannot attach non-LogWriter type! logWriter={logWriter}")
        self.logWriters.append(logWriter)

    def write(self, data: LogData) -> None:
        if not self.isInitialized:
            self.cachedLogs.append(data)
        else:
            for writer in self.logWriters:
                writer.write(data)

    def flush(self) -> None:
        if not self.isInitialized:
            raise Exception("Cannot flush to un-initialized Logger!")
        for writer in self.logWriters:
            writer.flush()

    def write_formatted(self, s: str, level: str, frame: FrameInfo = None) -> None:
        if frame is None:
            frame = FRAME(2)
        self.write(LogData(s, frame, level))

    def debug(self, s: str, frame: FrameInfo = None):
        self.write_formatted(s, DEBUG, frame)

    def info(self, s: str, frame: FrameInfo = None):
        self.write_formatted(s, INFO, frame)

    def warn(self, s: str, frame: FrameInfo = None):
        self.write_formatted(s, WARN, frame)

    def error(self, s: str, frame: FrameInfo = None):
        self.write_formatted(s, ERROR, frame)

    def fatal(self, s: str, frame: FrameInfo = None):
        self.write_formatted(s, FATAL, frame)
