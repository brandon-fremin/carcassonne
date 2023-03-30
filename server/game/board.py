from jsondata import jsondata
from tile import Tile
from typing import Dict

@jsondata
class Board:
    tiles: Dict[str, Tile]
