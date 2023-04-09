import traceback
import src.modules.logger as logger
from src.modules.timer import timer_cb
from src.server.server import Server

from src.game.tile import Tile
from src.game.tilemanifest import tile_manifest
from src.modules.jsondata import dumps
from src.game.game import Game
from src.game.settings import Settings
from src.modules.psuedorandom import PsuedoRandom

@timer_cb(logger.info)
def main():
    logger.initialize([
        logger.ColorizedLogWriter(), 
        logger.FileLogWriter("output.txt", "w"), 
        logger.FileLogWriter("output.debug.txt", "w", logger.DEBUG)
    ])
    
    # t = tile_manifest()[0]
    # print(dumps(t, indent=2))
    # t.rotate_90deg_ccw()
    # print(dumps(t, indent=2))
    server = Server()
    server.run()

    # g = Game(Settings(), PsuedoRandom())
    


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        tb = traceback.format_exc().strip()
        logger.warn(tb)
        logger.fatal(e)
