from src.modules.jsondata import jsondata
from src.game.tile import Tile
from typing import Dict

@jsondata
class Board:
    tiles: Dict[str, Tile]
