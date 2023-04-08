from src.game.meeple import Meeple
from src.modules.jsondata import jsondata, List, Optional, Enum
import src.modules.logger as logger


class FeatureType(Enum):
    Monastary: str = "Monastary"
    Road: str = "Road"
    City: str = "City"
    Field: str = "Field"


class Conn(Enum):
    RM: int = 0
    RT: int = 1
    TR: int = 2
    TM: int = 3
    TL: int = 4
    LT: int = 5
    LM: int = 6
    LB: int = 7
    BL: int = 8
    BM: int = 9
    BR: int = 10
    RB: int = 11


@jsondata
class Coordinate:
    x: int
    y: int


@jsondata
class Feature:
    componentId: Optional[str]
    svg: str
    type: FeatureType
    clickable: Coordinate
    connections: List[Conn]
    placeables: List[Meeple]

    def rotate_90deg_ccw(self):
        logger.warn("Feature.rotate_90deg_ccw() not implemented!")