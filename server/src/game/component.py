from src.modules.jsondata import jsondata, List
from src.game.types import FeatureType
from src.game.tile import Tile
from src.game.feature import Feature


@jsondata
class Node:
    tileId: str
    i: int
    j: int
    right: bool
    top: bool
    left: bool
    bottom: bool

    def __init__(self, tile: Tile, feature: Feature):
        assert type(tile) is Tile
        assert type(feature) is Feature
        self.tileId = tile.id
        self.i = tile.transform.i
        self.j = tile.transform.j
        self.right = any([c.is_right() for c in feature.connections])
        self.top = any([c.is_top() for c in feature.connections])
        self.left = any([c.is_left() for c in feature.connections])
        self.bottom = any([c.is_bottom() for c in feature.connections])

    def is_covered(self):
        return not (self.right or self.top or self.left or self.bottom)


@jsondata
class Component:
    id: str
    type: FeatureType
    value: int
    tileIds: List[str]
    features: List[Feature]
    isCompleted: bool

    def __init__(self, componentId: str, tiles: List[Tile]):
        assert type(componentId) == str
        for tile in tiles:
            assert type(tile) is Tile

        self.id = componentId
        self.type = None
        self.isCompleted = False
        self.value = 0
        self.tileIds = []
        self.features = []

        for tile in tiles:
            for feature in tile.features:
                if feature.componentId == self.id:
                    if not self.type:
                        self.type = feature.type
                    self.features.append(feature)
        self.update_tile_ids(tiles)
        self.update_is_completed(tiles)
        self.update_value()

    def __default_tile_ids(self):
        for feature in self.features:
            self.tileIds.append(feature.tileId)
        return list(set(self.tileIds))

    def __monastery_tile_ids(self, tiles: List[Tile]):
        def get_feature_tile():
            assert len(self.features) == 1
            feature = self.features[0]
            for tile in tiles:
                if tile.id == feature.tileId:
                    return tile
            raise Exception(
                f"Couldn't find tile '{feature.tileId}' in {tiles}")

        def tile_distance(a: Tile, b: Tile):
            if not a or not b:
                return 999  # this is good enough
            return max(abs(a.transform.i - b.transform.i),
                       abs(a.transform.j - b.transform.j))

        feature_tile = get_feature_tile()
        return [tile.id for tile in tiles if tile_distance(feature_tile, tile) <= 1]

    def update_tile_ids(self, tiles: List[Tile]):
        if self.type == FeatureType.Monastary:
            self.tileIds = self.__monastery_tile_ids(tiles)
        else:
            self.tileIds = self.__default_tile_ids()

    def update_is_completed(self, tiles: List[Tile]):
        if self.type == FeatureType.Monastary:
            return len(self.tileIds) == 9

        positions = set()
        for tile in tiles:
            positions.add((tile.transform.i, tile.transform.j))

        def get(tile_id):
            for tile in tiles:
                if tile.id == tile_id:
                    return tile
            raise Exception(f"Couldn't find tile id {tile_id} in {tiles}")

        nodes: List[Node] = []
        for feature in self.features:
            tile = get(feature.tileId)
            nodes.append(Node(tile, feature))
        

        for node in nodes:
            pass

            # TODO: IMPLEMENT!!!
        return False

    def __road_value(self):
        return len(self.tileIds)

    def __city_value(self):
        n = len(self.tileIds)
        return 2 * n if self.isCompleted else n

    def __monastery_value(self):
        n = len(self.tileIds)
        return n if self.isCompleted else n - 1

    def update_value(self):
        if self.type == FeatureType.Road:
            self.value = self.__road_value()
        elif self.type == FeatureType.City:
            self.value = self.__city_value()
        elif self.type == FeatureType.Monastary:
            self.value = self.__monastery_value()

    @staticmethod
    def calculate_from_tiles(tiles: List[Tile]):
        componentIds = []
        for tile in tiles:
            for feature in tile.features:
                componentIds.append(feature.componentId)
        componentIds = list(set(componentIds))
        return [Component(cid, tiles) for cid in componentIds]

    @staticmethod
    def make_id(idx: int):
        return f"component{idx}"
