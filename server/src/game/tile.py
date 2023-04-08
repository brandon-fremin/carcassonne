from src.modules.jsondata import jsondata, Optional
from src.game.sides import Sides
from src.game.transform import Transform
from src.game.feature import Feature
from typing import List


@jsondata
class Tile:
    id: str
    image: str
    transform: Transform
    sides: Sides
    features: List[Feature]
    numShields: int
    isGarden: bool

    def type(self) -> str:
        assert self.image.count(".") == 1
        return self.image.split(".")[0]
    
    def rotate_90deg_ccw(self):
        self.sides.right, self.sides.top, self.sides.left, self.sides.bottom = \
            self.sides.bottom, self.sides.right, self.sides.top, self.sides.left
        self.transform.rot = (self.transform.rot + 90) % 360
        for feature in self.features:
            feature.rotate_90deg_ccw()

