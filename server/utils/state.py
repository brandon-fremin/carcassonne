import json, random, os

from utils.tile import Tile, TILES_DIR, STATE_DIR
from utils.move import Move
from utils.get_legal_moves import get_legal_moves

class State:
    def client_json(self):
        pass

class State:
    def __init__(self,
        tiles,
        board,
        nextTile,
        legalMoves
    ):
        self.tiles: list[Tile] = tiles
        self.board: list[Tile]  = board
        self.nextTile: Tile = nextTile
        self.legalMoves: list[Move] = legalMoves

    def client_json(self):
        return {
            "board": [t.json() for t in self.board],
            "legalMoves": [m.json() for m in self.legalMoves],
            "nextTile": self.nextTile.json()
        }

    def save(self) -> State:
        json.dump([t.json() for t in self.tiles], open(f"{STATE_DIR}/tiles.json", "w"), indent=2)
        json.dump([t.json() for t in self.board], open(f"{STATE_DIR}/board.json", "w"), indent=2)
        json.dump(self.nextTile.json(), open(f"{STATE_DIR}/nextTile.json", "w"), indent=2)
        json.dump([m.json() for m in self.legalMoves], open(f"{STATE_DIR}/legalMoves.json", "w"), indent=2)  
        return self 

    def update_from_tiles(self) -> bool:
        self.board = list(filter(lambda tile: tile.isOnBoard(), self.tiles))
        if len(self.board) == len(self.tiles):
            return True  # game over
        otherTiles = list(filter(lambda tile: tile.isPlayable(), self.tiles))
        self.nextTile = random.choice(otherTiles)
        self.legalMoves = get_legal_moves(self.board, self.nextTile)
        return False

def get_state() -> State:
    tiles: list[Tile] = [
        Tile.load_json(data) 
        for data in json.load(open(f"{STATE_DIR}/tiles.json", "rb"))
    ]
    board = list(filter(lambda tile: tile.isOnBoard(), tiles))
    nextTile = Tile.load_json(
        json.load(open(f"{STATE_DIR}/nextTile.json", "rb"))
    )
    legalMoves = get_legal_moves(board, nextTile)
    return State(
        tiles,
        board,
        nextTile,
        legalMoves
    )