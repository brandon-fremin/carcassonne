from src.modules.jsondata import jsondata, List, Enum, enum_options
from src.game.tilemanifest import tile_manifest, TILE_DEFAULT_COUNTS, TILE_DEFAULT_GARDENS, tile_default_start
from src.game.tile import Tile
from src.game.types import Extension


@jsondata
class Settings:
    extensions: List[Extension]
    startTile: Tile
    numPlayers: int
    manifest: List[Tile]
    counts: List[int]

    def __init__(self, *args, **kwargs):
        assert len(args) == len(kwargs) == 0
        try:
            self.extensions = enum_options(Extension)
            self.startTile = tile_default_start()
            self.numPlayers = 0
            self.manifest = tile_manifest()
            self.counts = TILE_DEFAULT_COUNTS
        except:
            raise Exception()




