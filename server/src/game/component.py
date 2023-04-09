from src.modules.jsondata import jsondata, List
from src.game.types import FeatureType
from src.game.tile import Tile
from src.game.feature import Feature


@jsondata
class Component:
    id: str
    type: FeatureType
    value: int
    tileIds: List[str]
    features: List[Feature]

    def __init__(self, componentId: str, tiles: List[Tile]):
        assert type(componentId) == str
        for tile in tiles:
            assert type(tile) is Tile

        self.id = componentId
        self.type = None
        self.value = 0
        self.tileIds = []
        self.features = []

        for tile in tiles:
            for feature in tile.features:
                if feature.componentId == self.id:
                    if not self.type:
                        self.type = feature.type
                    self.features.append(feature)
        self.__update_value(tiles)

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

    def __is_completed(self, tiles: List[Tile]):
        if self.type == FeatureType.Monastary:
            return len(self.__monastery_tile_ids(tiles)) == 9

        # TODO: IMPLEMENT!!!
        return False

    def __road_value(self):
        self.tileIds = self.__default_tile_ids()
        return len(self.tileIds)

    def __city_value(self, tiles: List[Tile]):
        self.tileIds = self.__default_tile_ids()
        n = len(self.tileIds)
        return 2 * n if self.__is_completed(tiles) else n

    def __monastery_value(self, tiles: List[Tile]):
        self.tileIds = self.__monastery_tile_ids(tiles)
        if self.__is_completed(tiles):
            return len(self.tileIds)
        else:
            # no point for center square
            return len(self.tileIds) - 1

    def __update_value(self, tiles: List[Tile]):
        if self.type == FeatureType.Road:
            self.value = self.__road_value()
        elif self.type == FeatureType.City:
            self.value = self.__city_value(tiles)
        elif self.type == FeatureType.Monastary:
            self.value = self.__monastery_value(tiles)

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
