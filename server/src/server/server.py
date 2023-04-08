from flask import Flask, request as FlaskRequest
import random, traceback
import src.modules.logger as logger
from src.statemanager.statemanager import StateManager
from src.event.event import Event, InitializeGameEvent, MakeMoveEvent
from src.game.settings import Settings
from src.game.move import Move
from src.modules.jsondata import jsondata, asdict, Dict
from src.modules.timer import timer_cb
from time import sleep
from datetime import datetime


SERVER_PORT = 8080
FLASK_APP = Flask(__name__)
FLASK_CACHE: Dict[str, StateManager] = {}


def get_state_manager(session_id: str = None) -> StateManager:
    if session_id is None:
        state_manager = StateManager()
        session_id = state_manager.sessionId
        FLASK_CACHE[session_id] = state_manager
    elif session_id not in FLASK_CACHE.keys():
        state_manager = StateManager(session_id)
        FLASK_CACHE[session_id] = state_manager
    return FLASK_CACHE[session_id]


def middleware(func):
    @timer_cb(logger.info)
    def wrapper(*args, **kwargs):
        try:
            request = FlaskRequest.json
            logger.info(f"{func.__name__} - Request: {request}")
            response = func(*args, **kwargs)
        except Exception as e:
            tb = traceback.format_exc().strip()
            logger.warn(tb)
            logger.error(e)
            response = {"error": str(e)}
        logger.debug(f"Response: {response}")
        logger.flush()
        return response
    wrapper.__name__ = func.__name__
    return wrapper


def make_flask_event() -> Event:
    event = Event()
    event.timestamp = datetime.now().astimezone()
    event.senderId = str(FlaskRequest.remote_addr)
    return event


@jsondata
class GetGameRequest:
    sessionId: str

@jsondata
class NewGameRequest:
    settings: Settings

@jsondata
class NewGameResponse:
    sessionId: str

@jsondata
class MakeMoveRequest:
    sessionId: str
    move: Move


class Server:
    def __del__(self):
        for session_id, state_manager in FLASK_CACHE.items():
            logger.info(f"Savings state for session '{session_id}'")
            state_manager.save()

    def run(self):
        logger.info("Ready to server")
        FLASK_APP.run(port=SERVER_PORT)

    @FLASK_APP.route('/getGameSettings', methods=["GET", "PUT"])
    @middleware
    def getGameSettings():
        settings = Settings()
        response = asdict(settings)
        return response

    @FLASK_APP.route('/getGame', methods=["GET", "PUT"])
    @middleware
    def getGame():
        request = GetGameRequest(FlaskRequest.json)
        state = get_state_manager(request.sessionId)
        response = asdict(state.game)
        return response

    @FLASK_APP.route('/newGame', methods=["GET", "PUT"])
    @middleware
    def newGame():
        request = NewGameRequest(FlaskRequest.json)
        event = make_flask_event()
        event.payload = InitializeGameEvent(settings=request.settings)
        state = get_state_manager().handle(event).save()
        response = asdict(NewGameResponse(sessionId=state.sessionId))
        return response

    @FLASK_APP.route('/makeMove', methods=["GET", "PUT"])
    @middleware
    def makeMove():
        request = MakeMoveRequest(FlaskRequest.json)
        event = make_flask_event()
        event.payload = MakeMoveEvent(move=request.move)
        state = get_state_manager(request.sessionId).handle(event).save()
        response = asdict(state.game)
        return response

    @FLASK_APP.route('/poll', methods=["GET", "PUT"])
    @middleware
    def poll():
        sleep(15)
        response = {
            "data": f"Random Number: {random.random()}"
        }
        return response
