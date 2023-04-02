from src.modules.jsondata import jsondata
from enum import Enum


class Side(Enum):
    ROAD: str = "R"
    CITY: str = "C"
    FIELD: str = "F"



@jsondata
class Sides:
    left: Side
    right: Side
    top: Side
    bottom: Side
