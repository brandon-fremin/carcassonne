from utils.tile import Tile
from utils.move import Move

class FrontierTile:
    def __init__(self, i, j):
        self.i = i
        self.j = j
        self.searched = False
        self.isFrontier = True
    
    def json(self):
        return {
            "i": self.i,
            "j": self.j
        }

def expand(frontier: list[FrontierTile], i: int, j: int) -> list[dict]:
    # Make sure we don't already have tile
    for frontier_tile in frontier:
        if frontier_tile.i == i and frontier_tile.j == j:
            return frontier

    # Add tile to frontier
    frontier.append(FrontierTile(i, j))
    return frontier

def find(board: list[Tile], i: int, j: int) -> Tile:
    for tile in board:
        if tile.i == i and tile.j == j:
            return tile
    return None

def get_open_squares(board: list[Tile]) -> dict:
    frontier = [ FrontierTile(0, 0) ]

    old_frontier_size = 0
    while len(frontier) != old_frontier_size:
        old_frontier_size = len(frontier)

        # frontier is too large
        if len(frontier) > 1000:
            print(frontier)
            assert False
        

        for front_tile in frontier:
            if front_tile.searched:
                continue

            front_tile.searched = True
            i, j = front_tile.i, front_tile.j
            tile = find(board, i, j)
            if tile:
                front_tile.isFrontier = False
                frontier = expand(frontier, i - 1, j)
                frontier = expand(frontier, i + 1, j)
                frontier = expand(frontier, i, j - 1)
                frontier = expand(frontier, i, j + 1)

    return [
        front_tile.json()
        for front_tile in frontier
        if front_tile.isFrontier
    ]

def is_legal_top_bottom(top: Tile, bottom: Tile) -> bool:
    if top is None or bottom is None:
        return True
    return top.sides["bottom"] == bottom.sides["top"]

def is_legal_right_left(right: Tile, left: Tile) -> bool:
    if right is None or left is None:
        return True
    return right.sides["left"] == left.sides["right"]

def is_legal(board: list[Tile], nextTile: Tile, i: int, j: int) -> bool:
    left = find(board, i - 1, j)
    right = find(board, i + 1, j)
    bottom = find(board, i, j - 1)
    top = find(board, i, j + 1)
    return (
        is_legal_right_left(nextTile, left) and
        is_legal_right_left(right, nextTile) and
        is_legal_top_bottom(nextTile, bottom) and
        is_legal_top_bottom(top, nextTile)
    )

def get_legal_moves(board: list[Tile], nextTile: Tile) -> dict:
    open_squares = get_open_squares(board)
    rotations = [0, 90, 180, 270]
    legal_moves = []
    for square in open_squares:
        i, j = square["i"], square["j"]
        for rot in rotations:
            if is_legal(board, nextTile, i, j):
                legal_moves.append(Move(i, j, rot))
            nextTile.rotate_90deg_ccw()
    return legal_moves