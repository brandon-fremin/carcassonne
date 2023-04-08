from src.modules.jsondata import jsondata
from src.game.tile import Tile
from src.game.transform import Transform
from src.game.move import Move
from src.game.settings import Settings
from src.modules.psuedorandom import PsuedoRandom
from typing import Dict, List, Optional
import src.modules.logger as logger


@jsondata
class Node:
    i: int
    j: int
    isSearched: bool
    isFrontier: bool

    def __init__(self, i: int, j: int):
        assert type(i) is int
        assert type(j) is int
        self.i = i
        self.j = j
        self.isSearched = False
        self.isFrontier = True


@jsondata
class Board:
    nextTile: Optional[Tile]
    tiles: Dict[str, Tile]
    legalMoves: List[Move]
    drawStack: List[Tile]
    unplayableStack: List[Tile]
    frontier: List[Node]

    def __init__(self, settings: Settings, random: PsuedoRandom):
        assert type(settings) is Settings

        self.nextTile = None
        self.frontier = []
        self.tiles = {}
        self.legalMoves = []
        self.drawStack = []
        self.unplayableStack = []
        for template_tile, count in zip(settings.manifest, settings.counts):
            for i in range(count):
                tile = Tile(template_tile)
                tile_type = tile.type()
                tile.id = f"{tile_type}_{i}"
                if tile_type == settings.startTile.type() and len(self.tiles) == 0:
                    tile.transform = Transform(i=0, j=0, rot=0)
                    self.tiles[tile.id] = tile
                else:
                    self.drawStack.append(tile)
        # populates: nextTile, frontier, and legalMoves
        self.update_next_tile(random)

        logger.info(f"Board initialized from settings: {self.board_stats()}")

    def update_next_tile(self, random: PsuedoRandom):
        # populates: nextTile, frontier, and legalMoves
        self.nextTile = random.choice(self.drawStack)
        self.drawStack.remove(self.nextTile)
        self.calculate_legal_moves()  # populates: frontier, legalMoves

    def make_move(self, move: Move, random: PsuedoRandom):
        assert type(move) is Move
        assert move.tileId == self.nextTile.id

        # put palced tile on board
        self.nextTile.rotate_ccw(move.transform.rot)
        self.nextTile.transform = move.transform
        self.tiles[self.nextTile.id] = self.nextTile
        self.nextTile = None

        # reset unplayable stack
        self.drawStack.extend(self.unplayableStack)
        self.unplayableStack = []

        # populates: nextTile, frontier, and legalMoves
        self.update_next_tile(random)

        logger.info(f"Board updated: {self.board_stats()}")

    def board_stats(self):
        n_total = (len(self.tiles) + len(self.drawStack) +
                   len(self.unplayableStack) + (1 if self.nextTile else 0))
        n_frontier = sum([1 if f.isFrontier else 0 for f in self.frontier])
        return (
            f"[ #total={n_total} "
            f"#drawStack={len(self.drawStack)} "
            f"#placed={len(self.tiles)} "
            f"#frontier={n_frontier}/{len(self.frontier)} "
            f"#legalMoves={len(self.legalMoves)} "
            f"nextTile.id={self.nextTile.id} ]"
        )

    def calculate_legal_moves(self) -> dict:
        assert type(self.nextTile) is Tile
        self.calculate_frontier()

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

    def calculate_frontier(self):
        if len(self.frontier) == 0:
            self.frontier = [Node(i=0, j=0)]
        for node in self.frontier:
            node.isSearched = False

        def find(i: int, j: int) -> bool:
            for tile in self.tiles.values():
                if tile.transform.i == i and tile.transform.j == j:
                    return True
            return False

        def expand(i: int, j: int) -> list[dict]:
            # Make sure we don't already have this node
            for node in self.frontier:
                if node.i == i and node.j == j:
                    return
            # Add tile to frontier
            self.frontier.append(Node(i=i, j=j))

        n = 0
        while len(self.frontier) > n:
            n = len(self.frontier)

            for node in self.frontier:
                if node.isSearched:
                    continue

                node.isSearched = True
                i, j = node.i, node.j
                tile = find(i, j)
                if tile:
                    node.isFrontier = False
                    expand(i - 1, j)
                    expand(i + 1, j)
                    expand(i, j - 1)
                    expand(i, j + 1)
