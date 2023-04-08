from src.modules.jsondata import jsondata, Enum


class Side(Enum):
    Road: str = "Road"
    City: str = "City"
    Field: str = "Field"



@jsondata
class Sides:
    left: Side
    right: Side
    top: Side
    bottom: Side
    