from src.game.tile import Tile
from src.game.frontier import Frontier
from src.game.types import Move
from src.modules.jsondata import List, Dict


def get_legal_moves(tile: Tile, board_tiles: Dict[str, Tile], frontier: Frontier) -> List[Move]:
    tile = Tile(tile)  # Deep copy!

    def find(i, j) -> bool:
        tile_id = frontier.tile_id_at(i, j)
        if tile_id is None:
            return None
        return board_tiles[tile_id]

    def legal_top_bottom(t: Tile, b: Tile) -> bool:
        return t is None or b is None or t.sides.bottom == b.sides.top

    def legal_right_left(r: Tile, l: Tile) -> bool:
        return r is None or l is None or r.sides.left == l.sides.right

    def is_legal(i: int, j: int) -> bool:
        left = find(i - 1, j)
        right = find(i + 1, j)
        bottom = find(i, j - 1)
        top = find(i, j + 1)
        return (
            legal_right_left(tile, left) and
            legal_right_left(right, tile) and
            legal_top_bottom(tile, bottom) and
            legal_top_bottom(top, tile)
        )

    rotations = [0, 90, 180, 270]
    legal_moves = []
    for node in frontier.frontier_nodes():
        i, j = node.i, node.j
        for rot in rotations:
            if is_legal(i, j):
                legal_moves.append(Move(tile.id, i, j, rot))
            tile.rotate_90deg_ccw()

    return legal_moves