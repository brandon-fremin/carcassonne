from utils.state import State 
from utils.tile import Tile, TILES_DIR
from utils.get_legal_moves import get_legal_moves
import random, os

def handle_new_game(request: dict) -> dict:
    tiles: list[Tile] = []
    for (_, _, files) in os.walk(TILES_DIR):
        for f in files:
            tiles.extend(Tile.load_tiles_from_file(f))
    board = list(filter(lambda tile: tile.isOnBoard(), tiles))
    otherTiles = list(filter(lambda tile: tile.isPlayable(), tiles))
    nextTile = random.choice(otherTiles)
    legalMoves = get_legal_moves(board, nextTile)

    state = State(
        tiles,
        board,
        nextTile,
        legalMoves
    )
    state.save()

    return state.client_json()