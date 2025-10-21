from src.modules.jsondata import jsondata, dumps
from src.game.tile import Tile
from src.game.settings import Settings
from src.game.types import Meeple, Move, Transform
from src.game.feature import Feature, Conn
#from src.game.component import Component
from src.game.componentmap import ComponentMap, Component
from src.modules.psuedorandom import PsuedoRandom
from src.game.frontier import Frontier
from typing import Dict, List, Optional
import src.modules.logger as logger
from src.game.board_implementation.getlegalmoves import get_legal_moves
from src.modules.timer import timer_cb


@jsondata
class Board:
    nextTile: Optional[Tile]
    lastTileId: Optional[str]
    tiles: Dict[str, Tile]
    drawStack: List[Tile]
    unplayableStack: List[Tile]
    legalMoves: List[Move]
    components: Dict[str, Component]
    frontier: Frontier
    componentMap: ComponentMap

    def __init__(self, settings: Settings, random: PsuedoRandom):
        assert type(settings) is Settings
        assert type(random) is PsuedoRandom

        self.nextTile = None
        self.lastTileId = None
        self.frontier = Frontier()
        self.componentMap = ComponentMap()
        self.tiles = {}
        self.legalMoves = []
        self.drawStack = []
        self.unplayableStack = []
        self.components = {}
        counter = 0
        for template_tile, count in zip(settings.manifest, settings.counts):
            for i in range(count):
                tile = Tile(template_tile)
                tile.id = f"tile{counter}_{tile.image}_{i}"
                counter += 1
                if tile.image == settings.startTile.image and len(self.tiles) == 0:
                    tile.transform = Transform(i=0, j=0, rot=0)
                    self.nextTile = tile
                else:
                    self.drawStack.append(tile)
                for feature in tile.features:
                    feature.tileId = tile.id

        # populates: nextTile, frontier, components, and legalMoves
        self.place_tile(
            Move(tileId=self.nextTile.id, transform=self.nextTile.transform),
            random)

        logger.info(f"Board initialized from settings: {self.board_stats()}")

    def update_next_tile(self, random: PsuedoRandom):
        # populates: nextTile, frontier, and legalMoves
        self.nextTile = random.choice(self.drawStack)
        self.drawStack.remove(self.nextTile)
        self.legalMoves = get_legal_moves(self.nextTile, self.tiles, self.frontier)

    def redraw_tile(self, tileId: str, random: PsuedoRandom):
        # verify inputs
        assert type(tileId) is str
        assert type(random) is PsuedoRandom
        assert tileId == self.nextTile.id
        assert len(self.legalMoves) == 0

        # make next tile unplayable and redraw
        self.unplayableStack.append(self.nextTile)
        self.update_next_tile()

        logger.info(f"Board.redraw_tile: {self.board_stats()}")

    @timer_cb(logger.info)
    def place_tile(self, move: Move, random: PsuedoRandom):
        # verify inputs
        assert type(move) is Move
        assert type(random) is PsuedoRandom
        assert move.tileId == self.nextTile.id

        # put placed nextTile on board
        placedTile = self.nextTile
        placedTile.set_transform(move.transform)
        self.tiles[placedTile.id] = placedTile
        self.frontier.push(placedTile)
        self.componentMap.push(placedTile)
        self.lastTileId = placedTile.id
        self.components = self.componentMap.get_components()

        # reset unplayable stack and get next tile
        self.drawStack.extend(self.unplayableStack)
        self.unplayableStack = []
        self.update_next_tile(random)

        logger.info(f"Board.place_tile: {self.board_stats()}")

    def place_meeple(self, tileId: str, featureId: str, meeple: Meeple):
        # verify inputs
        assert type(tileId) is str
        assert type(featureId) is str
        assert tileId == self.lastTileId
        lastTile = self.tiles[self.lastTileId]
        assert any([f.id == featureId for f in lastTile.features])
        feature = [f for f in lastTile.features if f.id == featureId][0]
        assert feature.can_place_meeple(meeple)

        # add meeple to feature
        feature.meeples.append(meeple)

        logger.info(f"Board.place_meeple: {self.board_stats()}")

    def board_stats(self):
        n_total = (len(self.tiles) + len(self.drawStack) +
                   len(self.unplayableStack) + (1 if self.nextTile else 0))
        return (
            f"[ #total={n_total} "
            f"#drawStack={len(self.drawStack)} "
            f"#placed={len(self.tiles)} "
            f"#frontier={self.frontier.size()}/{len(self.frontier.nodes)} "
            f"#legalMoves={len(self.legalMoves)} "
            f"nextTile.id={self.nextTile.id} ]"
        )

    # def update_components(self):
    #     def get(i: int, j: int):
    #         for tile in self.tiles.values():
    #             if tile.transform.i == i and tile.transform.j == j:
    #                 return tile
    #         return None

    #     def neighbors(i: int, j: int):
    #         return [
    #             get(i + 1, j),  # right
    #             get(i, j + 1),  # top
    #             get(i - 1, j),  # left
    #             get(i, j - 1)  # bottom
    #         ]

    #     def union_right_left(right: Feature, left: Feature):
    #         r_cons = right.connections
    #         l_cons = left.connections
    #         res = set()
    #         if (
    #             (Conn.LT in r_cons and Conn.RT in l_cons) or
    #             (Conn.LM in r_cons and Conn.RM in l_cons) or
    #             (Conn.LB in r_cons and Conn.RB in l_cons)
    #         ):
    #             res.add(right.componentId)
    #             res.add(left.componentId)
    #         return res

    #     def union_top_bottom(top: Feature, bottom: Feature):
    #         t_cons = top.connections
    #         b_cons = bottom.connections
    #         res = set()
    #         if (
    #             (Conn.BL in t_cons and Conn.TL in b_cons) or
    #             (Conn.BM in t_cons and Conn.TM in b_cons) or
    #             (Conn.BR in t_cons and Conn.TR in b_cons)
    #         ):
    #             res.add(top.componentId)
    #             res.add(bottom.componentId)
    #         return res

    #     def meld_components(newId, componentIds):
    #         for tile in self.tiles.values():
    #             for feature in tile.features:
    #                 if feature.componentId in componentIds:
    #                     feature.componentId = newId

    #     def assign_component(feature: Feature, tile: Tile):
    #         right, top, left, bottom = neighbors(
    #             tile.transform.i, tile.transform.j)
    #         componentIds = set()
    #         if right:
    #             for other_feature in right.features:
    #                 componentIds = componentIds.union(
    #                     union_right_left(other_feature, feature))
    #         if left:
    #             for other_feature in left.features:
    #                 componentIds = componentIds.union(
    #                     union_right_left(feature, other_feature))
    #         if top:
    #             for other_feature in top.features:
    #                 componentIds = componentIds.union(
    #                     union_top_bottom(other_feature, feature))
    #         if bottom:
    #             for other_feature in bottom.features:
    #                 componentIds = componentIds.union(
    #                     union_top_bottom(feature, other_feature))
    #         componentIds = set(
    #             [cid for cid in componentIds if cid is not None])

    #         if len(componentIds) == 1:
    #             feature.componentId = list(componentIds)[0]
    #         else:
    #             feature.componentId = Component.make_id(self.nextComponentIdx)
    #             self.nextComponentIdx += 1
    #         meld_components(feature.componentId, componentIds)

    #     for tile in self.tiles.values():
    #         for feature in tile.features:
    #             if feature.componentId is None:
    #                 assign_component(feature, tile)
    #     self.components = Component.calculate_from_tiles(self.tiles.values())


