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
                tile.id = f"tile{str(counter).zfill(3)}_{tile.image}_{i}"
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

    def completed_component_ids(self):
        return [
            component_id
            for component_id, component in self.components.items()
            if component.isCompleted
        ]

    def num_features(self):
        return sum([
            len(nodes)
            for nodes in self.componentMap.nodes.values()
        ])

    def board_stats(self):
        n_total = (len(self.tiles) + len(self.drawStack) +
                   len(self.unplayableStack) + (1 if self.nextTile else 0))
        return (
            f"[ #total={n_total} "
            f"#drawStack={len(self.drawStack)} "
            f"#placed={len(self.tiles)} "
            f"#frontier={self.frontier.size()}/{len(self.frontier.nodes)} "
            f"#components={len(self.completed_component_ids())}/{len(self.components)} "
            f"#features={self.num_features()} "
            f"#legalMoves={len(self.legalMoves)} "
            f"nextTile.id={self.nextTile.id} ]"
        )
