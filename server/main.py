import traceback
import src.modules.logger as logger
from src.modules.timer import timer_cb
from src.server.server import Server


@timer_cb(logger.info)
def main():
    logger.initialize([
        logger.ColorizedLogWriter(), 
        logger.FileLogWriter("output.txt", "w"), 
        logger.FileLogWriter("output.debug.txt", "w", logger.DEBUG)
    ])
    server = Server()
    server.run()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        tb = traceback.format_exc().strip()
        logger.warn(tb)
        logger.fatal(e)
