import logging
from src.server.server import Server
from src.common.lokilogger import configure_logging


logger = logging.getLogger(__name__)


def main():
    configure_logging(logging.DEBUG)
    server = Server()
    server.run()


if __name__ == "__main__":
    main()