from src.game.types import Meeple, MeepleType, FeatureType
from src.modules.jsondata import jsondata, List, Optional, Enum
import src.modules.logger as logger


class Conn(Enum):
    RB: int = 0
    RM: int = 1
    RT: int = 2
    TR: int = 3
    TM: int = 4
    TL: int = 5
    LT: int = 6
    LM: int = 7
    LB: int = 8
    BL: int = 9
    BM: int = 10
    BR: int = 11

    @staticmethod
    def rotate_90deg_ccw(conn):
        return Conn((conn.value + 3) % 12)


@jsondata
class Coordinate:
    x: int
    y: int

    def rotate_90deg_ccw(self):
        temp_x = self.x - 50
        temp_y = self.y - 50
        temp_x, temp_y = -temp_y, temp_x
        self.x = temp_x + 50
        self.y = temp_y + 50


def svg_rotate_90deg_ccw(svg):
    return svg


ALLOWABLE_PLACEMENTS = {
    FeatureType.Road: [MeepleType.Basic],
    FeatureType.Field: [MeepleType.Basic],
    FeatureType.City: [MeepleType.Basic],
    FeatureType.Monastary: [MeepleType.Basic, MeepleType.Abbot],
    FeatureType.Garden: [MeepleType.Abbot],
}


@jsondata
class Feature:
    id: str
    tileId: Optional[str]
    componentId: Optional[str]
    svg: str
    type: FeatureType
    clickable: Coordinate
    connections: List[Conn]
    meeples: List[Meeple]

    def rotate_90deg_ccw(self):
        self.clickable.rotate_90deg_ccw()
        self.svg = svg_rotate_90deg_ccw(self.svg)
        self.connections = [
            Conn.rotate_90deg_ccw(conn) for conn in self.connections
        ]

    def can_place_meeple(self, meeple: Meeple):
        assert self.type in ALLOWABLE_PLACEMENTS.keys()
        return meeple.type in ALLOWABLE_PLACEMENTS[self.type]