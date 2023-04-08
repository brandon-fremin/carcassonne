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
        return self.image
    
    def rotate_90deg_ccw(self):
        self.sides.right, self.sides.top, self.sides.left, self.sides.bottom = \
            self.sides.bottom, self.sides.right, self.sides.top, self.sides.left
        self.transform.rot = (self.transform.rot + 90) % 360
        for feature in self.features:
            feature.rotate_90deg_ccw()

    def rotate_ccw(self, deg):
        assert deg % 90 == 0
        for _ in range(deg // 90):
            self.rotate_90deg_ccw()

