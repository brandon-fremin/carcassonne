from src.modules.jsondata import jsondata
from typing import Dict, List
from src.game.board import Board
from src.game.player import Player
from src.game.event import Event


@jsondata
class State:
    board: Board
    players: Dict[str, Player]
    startTileId: str
    playerTurnId: str
    turnNumber: int
    history: List[Event]
