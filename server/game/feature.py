from typing import List, Dict
from meeple import Meeple
from jsondata import jsondata


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
