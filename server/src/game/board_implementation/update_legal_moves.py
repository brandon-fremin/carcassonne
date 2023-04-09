from src.game.types import Move, Transform
from src.game.tile import Tile


def update_legal_moves(self):
    assert type(self.nextTile) is Tile
    self.update_frontier()

    def find(i, j) -> bool:
        for tile in self.tiles.values():
            if tile.transform.i == i and tile.transform.j == j:
                return tile
        return None

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
            legal_right_left(self.nextTile, left) and
            legal_right_left(right, self.nextTile) and
            legal_top_bottom(self.nextTile, bottom) and
            legal_top_bottom(top, self.nextTile)
        )

    rotations = [0, 90, 180, 270]
    self.legalMoves = []
    for node in self.frontier:
        if node.isFrontier:
            i, j = node.i, node.j
            for rot in rotations:
                if is_legal(i, j):
                    move = Move()
                    move.tileId = self.nextTile.id
                    move.transform = Transform(i=i, j=j, rot=rot)
                    self.legalMoves.append(move)
                self.nextTile.rotate_90deg_ccw()
