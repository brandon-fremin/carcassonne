from typing import List, Tuple
from tile import *
import random

def start_tile():
    return TileD().set_i(0).set_j(0)

def tile_manifest():
    return [
        TileA(), TileA(),
        TileB(), TileB(), TileB(), TileB(),
        TileC(),
        TileD(), TileD(), TileD(), TileD(),
        TileE(is_garden=True), TileE(), TileE(),TileE(), TileE(),
        TileF(), TileF(),
        TileG(),
        TileH(is_garden=True), TileH(),  TileH(), 
        TileI(is_garden=True), TileI(),
        TileJ(), TileJ(), TileJ()
    ]

class State:
    _board_tiles: List[Tile]
    _draw_tiles: List[Tile]
    _start_tiles: List[Tile]

    def __init__(self):
        self._board_tiles = [start_tile()]
        self._draw_tiles = tile_manifest()
        random.shuffle(self._draw_tiles)
        self._start_tiles = []

    def __str__(self):
        return f"{len(self._draw_tiles)}"

    def board(self) -> List[Tile]:
        return self._board_tiles
    
    def next_tile(self) -> Tile:
        return self._board_tiles[0]
    
    def num_tiles_remaining(self) -> int:
        return len(self._draw_tiles) + len(self._start_tiles)