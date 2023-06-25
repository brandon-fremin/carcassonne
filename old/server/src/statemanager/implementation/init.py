from src.modules.jsondata import jsondata, Enum
from src.modules.psuedorandom import PsuedoRandom
from src.game.game import Game
import json


class GameState(Enum):
    Uninitialized: str = "Uninitialized"
    Waiting: str = "Waiting"


def init_implementation(self, *args, **kwargs):
    if len(args) == len(kwargs) == 0:
        initialize_default(self)
    elif len(args) == 1 and len(kwargs) == 0 and type(args[0]) is str:
        initialize_by_session_id(self, args[0])
    else:
        raise AssertionError(
            f"Invalid input arguments: args={args} kwargs={kwargs}")

def initialize_default(self):
    self.sessionId = PsuedoRandom.id()
    self.state = GameState.Uninitialized
    self.random = PsuedoRandom(PsuedoRandom.uuid())
    self.game = Game(self.random)
    self.agents = []
    self.history = []

def initialize_by_session_id(self, session_id: str):
    with open(self.session_file(session_id), "rb") as session_fp:
        self.__init__(json.load(session_fp))