DEBUG = "DEBUG"
INFO = "INFO"
WARN = "WARN"
ERROR = "ERROR"
FATAL = "FATAL"

DEFAULT_LEVEL = INFO

LEVELS = {
    DEBUG: 10,
    INFO: 20,
    WARN: 30,
    ERROR: 40,
    FATAL: 50
}

LEVELS_MAX_STR_LEN = max([
    len(level) for level in LEVELS.keys()
])