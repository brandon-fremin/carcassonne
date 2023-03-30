
from jsondata import jsondata
from sides import Sides
from transform import Transform
from feature import Feature
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
