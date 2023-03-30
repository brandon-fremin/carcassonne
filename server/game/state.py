
from jsondata import jsondata
from typing import Dict, List
from board import Board
from player import Player
from event import Event

@jsondata
class State:
    board: Board
    players: Dict[str, Player]
    startTileId: str
    playerTurnId: str
    turnNumber: int
    history: List[Event]

