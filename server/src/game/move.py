from src.modules.jsondata import jsondata
from src.game.transform import Transform


@jsondata
class Move:
    tileId: str
    transform: Transform

    def __init__(self, tid):
        self.tileId = tid
        self.transform = Transform()
