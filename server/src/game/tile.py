from src.modules.jsondata import jsondata
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
