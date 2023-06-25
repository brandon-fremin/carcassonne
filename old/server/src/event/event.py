from datetime import datetime
from src.modules.jsondata import jsondata, Union
from src.game.settings import Settings
from src.game.types import Move


@jsondata
class InitializeGameEvent:
    settings: Settings


@jsondata
class PlaceTileEvent:
    move: Move


@jsondata
class PlaceMeepleEvent:
    tileId: str
    featureId: str


@jsondata
class Event:
    timestamp: datetime
    senderId: str
    payload: Union[
                    InitializeGameEvent, 
                    PlaceTileEvent
                ]
