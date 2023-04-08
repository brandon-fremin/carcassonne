from src.modules.jsondata import jsondata
from src.game.transform import Transform


@jsondata
class Move:
    tileId: str
    transform: Transform
