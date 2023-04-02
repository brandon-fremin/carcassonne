from typing import MutableSet
from io import TextIOWrapper
from src.modules.logger_implemenation.logger_macros import *
from src.modules.logger_implemenation.logger_logdata import *
from typing import Callable


class LogWriter:
    writeLevels: MutableSet[str]
    formatter: Callable[[LogData], str]

    def __init__(self,
                 level: str = DEFAULT_LEVEL
                 ):
        level_int = LEVELS.get(level, 0)
        self.writeLevels = set([
            l for l in
            filter(lambda key: LEVELS[key] >= level_int,
                   LEVELS.keys())
        ])

    def write(self, data: LogData) -> None:
        pass

    def flush(self) -> None:
        pass


class StdoutLogWriter(LogWriter):
    def write(self, data: LogData) -> None:
        if data.level not in self.writeLevels:
            return
        print(self.formatter(data), end='')

    def flush(self) -> None:
        print(end='', flush=True)


class ColorizedLogWriter(StdoutLogWriter):
    def __init__(self,
                 level: str = DEFAULT_LEVEL,
                 formatter: Callable[[LogData], str] = stdout_formatter
                 ):
        def colorized_formatter(data: LogData):
            return ColorizedLogWriter.stdout_colorize(
                formatter(data), data.level)
        self.formatter = colorized_formatter
        super().__init__(level)

    def stdout_colorize(s: str, level: str) -> str:
        if level in [WARN]:
            return Fore.YELLOW + s + Style.RESET_ALL
        elif level in [ERROR, FATAL]:
            return Fore.RED + s + Style.RESET_ALL
        else:
            return s


class FileLogWriter(LogWriter):
    fp: TextIOWrapper

    def __init__(self,
                 file: str,
                 mode: str = "a",
                 level: str = DEFAULT_LEVEL,
                 formatter: Callable[[LogData], str] = logfile_formatter
                 ):
        self.fp = open(file, mode)
        self.formatter = formatter
        super().__init__(level)

    def __del__(self):
        if self.fp:
            self.fp.close()

    def write(self, data: LogData) -> None:
        if data.level not in self.writeLevels:
            return
        self.fp.write(self.formatter(data))

    def flush(self) -> None:
        self.fp.flush()
