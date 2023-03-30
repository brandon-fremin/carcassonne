from jsondata import jsondata
from transform import Transform
from typing import List, Dict, Union


@jsondata
class Move:
    tileId: str
    transform: Transform
