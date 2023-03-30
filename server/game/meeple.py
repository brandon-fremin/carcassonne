from dataclasses import dataclass
from jsondata import jsondata

@jsondata
class Meeple:
    name: str
    image: str