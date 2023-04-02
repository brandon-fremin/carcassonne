from typing import List
from src.game.meeple import Meeple
from src.modules.jsondata import jsondata


@jsondata
class Feature:
    id: str
    svg: str
    type: str
    clickableX: int
    clickableY: int
    placeables: List[Meeple]

    def hello(self):
        print("Hello World")
