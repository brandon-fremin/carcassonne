import os

CF_ACCESS_CLIENT_ID: str  = os.getenv("CF_ACCESS_CLIENT_ID")
CF_ACCESS_CLIENT_SECRET: str = os.getenv("CF_ACCESS_CLIENT_SECRET")

IOT_SERVER_HOST: str = "iot.brandonfremin.com"
LOKI_HOST: str = "localhost"
LOKI_PORT: int = 3100
LOKI_BATCH_SIZE: int = 50
LOKI_PING_TIMEOUT: float = 5.0

APP_NAME: str = "carcassonne"
SERVER_HOST: str = "localhost"
SERVER_PORT: int = 8080
MACHINE_NAME: str = os.getenv("COMPUTERNAME", os.getenv("HOSTNAME", "unknown"))
USERNAME: str = os.getenv("USERNAME", os.getenv("USER", "anonymous"))
TZ: str = os.getenv("TZ", "America/New_York")

DISABLED_LOGGERS: list[str] = ["urllib3", "requests", "asyncio", "cassandra"]
LOGGER_FORMAT: str = "%(asctime)s.%(msecs)03d %(name)s:%(lineno)d [%(levelname)s] %(message)s"
LOGGER_DATEFMT: str = "%Y-%m-%dT%H:%M:%S"