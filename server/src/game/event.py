from datetime import datetime
from src.modules.jsondata import jsondata
from typing import Union

@jsondata
class Event:
    timestamp: datetime
    senderId: str
    payload: Union[None, str]

