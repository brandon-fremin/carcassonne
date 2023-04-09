from src.modules.jsondata import jsondata, List, Enum, dumps, asdict
from src.agent.agent import Agent
from src.event.event import Event, InitializeGameEvent, PlaceTileEvent
from src.game.game import Game
from src.modules.psuedorandom import PsuedoRandom
import os
import json
import traceback
import src.modules.logger as logger
from src.modules.timer import timer_cb


PWD = os.path.dirname(os.path.realpath(__file__))
STATE_DIR = os.path.join(PWD, "state")
if not os.path.exists(STATE_DIR):
    os.mkdir(STATE_DIR)


class GameState(Enum):
    Uninitialized: str = "Uninitialized"
    WaitingPlaceTile: str = "WaitingPlaceTile"
    WaitingPlaceMeeple: str = "WaitingPlaceMeeple"        


@jsondata
class StateManager:
    sessionId: str
    random: PsuedoRandom
    fsaState: GameState
    game: Game
    agents: List[Agent]
    history: List[Event]

    def __init__(self, *args, **kwargs):
        if len(args) == len(kwargs) == 0:
            self.initialize_default()
        elif len(args) == 1 and len(kwargs) == 0 and type(args[0]) is str:
            self.initialize_by_session_id(args[0])
        else:
            raise AssertionError(
                f"Invalid input arguments: args={args} kwargs={kwargs}")

    def initialize_default(self):
        self.sessionId = PsuedoRandom.id()
        self.fsaState = GameState.Uninitialized
        self.random = PsuedoRandom(PsuedoRandom.uuid())
        self.game = Game()
        self.agents = []
        self.history = []

    def initialize_by_session_id(self, session_id: str):
        with open(self.session_file(session_id), "rb") as session_fp:
            self.__init__(json.load(session_fp))

    @staticmethod
    def session_file(session_id: str) -> str:
        return os.path.join(STATE_DIR, f'session.{session_id}.json')

    def save(self):
        with open(StateManager.session_file(self.sessionId), "w") as session_fp:
            data = dumps(self, indent=2)
            session_fp.write(data)
        return self

    def __handle_initialize_game_event(self, event: Event):
        assert type(event.payload) is InitializeGameEvent
        assert self.fsaState == GameState.Uninitialized
        settings = event.payload.settings
        self.game = Game(settings, self.random)
        self.agents = [Agent(i) for i in range(settings.numPlayers)]
        self.fsaState = GameState.WaitingPlaceTile

    def __handle_place_tile_event(self, event: Event):
        assert type(event.payload) is PlaceTileEvent
        #assert self.fsaState == GameState.WaitingPlaceTile
        self.game.board.place_tile(event.payload.move, self.random)
        #self.fsaState = GameState.WaitingPlaceMeeple
    
    def __handle_place_meeple_event(self, event: Event):
        assert type(event.payload) is PlaceTileEvent
        assert self.fsaState == GameState.WaitingPlaceMeeple
        self.game.board.place_meeple(event.payload.move, self.random)
        self.fsaState = GameState.WaitingPlaceTile

    def __handle(self, event: Event):
        logger.info(
            f"Event from '{event.senderId}' at {event.timestamp.isoformat()}")
        payload = event.payload
        if type(payload) is InitializeGameEvent:
            self.__handle_initialize_game_event(event)
        elif type(payload) is PlaceTileEvent:
            self.__handle_place_tile_event(event)
        else:
            raise TypeError(f"Unknown payload: {payload}")

    @timer_cb(logger.info)
    def handle(self, event: Event):
        snapshot = asdict(self)
        try:
            assert type(event) is Event
            self.__handle(event)
            self.history.append(event)
        except Exception as e:
            logger.warn(traceback.format_exc().strip())
            logger.error(
                f"Exception thrown while processing\nEvent={event}\nException={e}")
            logger.debug("Restoring state from beginning of handle()")
            self.__init__(snapshot)
        return self
