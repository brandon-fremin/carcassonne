from dataclasses import dataclass
from jsondata import jsondata

@jsondata
class Event:
    data: str

