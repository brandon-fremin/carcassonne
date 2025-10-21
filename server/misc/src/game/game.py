from src.modules.jsondata import jsondata, Enum, enum_options, List
from src.game.board import Board
from src.game.types import Avatar, Color, Move
from src.game.settings import Settings
from src.modules.psuedorandom import PsuedoRandom


@jsondata
class Game:
    settings: Settings
    board: Board
    turn: int
    avatars: List[Avatar]

    def __init__(self, settings: Settings, random: PsuedoRandom):
        assert type(settings) is Settings
        assert type(random) is PsuedoRandom

        self.settings = settings
        self.board = Board(settings, random)
        self.turn = 0
        colors = enum_options(Color)
        self.avatars = [
            Avatar(f"Player {i}", colors[i])
            for i in range(settings.numPlayers)
        ]

    def place_tile(self, move: Move, random: PsuedoRandom):
        self.board.place_tile(move, random)
