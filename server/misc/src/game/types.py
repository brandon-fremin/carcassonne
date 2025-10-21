from src.modules.jsondata import jsondata, Enum, enum_options, List


class Color(Enum):
    Red: str = "Red"
    Blue: str = "Blue"
    Yellow: str = "Yellow"
    Green: str = "Green"


class MeepleType(Enum):
    Basic: str = "Basic"
    Abbot: str = "Abbot"


class Side(Enum):
    Road: str = "Road"
    City: str = "City"
    Field: str = "Field"


class Extension(Enum):
    Farmers: str = "Farmers"
    # Abbot: str = "Abbot"
    # River: str = "River"
    # InnAndCathedrals: str = "Inn and Cathedrals"


class FeatureType(Enum):
    Monastary: str = "Monastary"
    Road: str = "Road"
    City: str = "City"
    Field: str = "Field"
    Garden: str = "Garden"


@jsondata
class Meeple:
    type: MeepleType
    color: Color
    image: str
    

@jsondata
class Transform:
    i: int
    j: int
    rot: int


@jsondata
class Sides:
    left: Side
    right: Side
    top: Side
    bottom: Side


@jsondata
class Move:
    tileId: str
    transform: Transform

    def __init__(self, tileId: str, i: int = 0, j: int = 0, rot: int = 0):
        assert type(tileId) is str
        assert type(i) is int
        assert type(j) is int
        assert type(rot) is int
        self.tileId = tileId
        self.transform = Transform(i=i, j=j, rot=rot)


@jsondata
class Avatar:
    name: str
    color: Color
    score: int

    def __init__(self, name: str, color: Color):
        assert type(name) is str
        assert type(color) is Color
        self.name = name
        self.color = color
        self.score = 0
