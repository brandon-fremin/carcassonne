from datetime import datetime
from src.modules.jsondata import jsondata, Union
from src.game.settings import Settings
from src.game.move import Move


@jsondata
class InitializeGameEvent:
    settings: Settings


@jsondata
class MakeMoveEvent:
    move: Move


@jsondata
class Event:
    timestamp: datetime
    senderId: str
    payload: Union[
                    InitializeGameEvent, 
                    MakeMoveEvent
                ]
