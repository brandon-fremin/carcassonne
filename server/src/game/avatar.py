from src.modules.jsondata import jsondata, enum_options, List, Enum
from src.game.settings import Settings


class Color(Enum):
    Red: str = "Red"
    Blue: str = "Blue"
    Yellow: str = "Yellow"
    Green: str = "Green"


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

        
