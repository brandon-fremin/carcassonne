from src.modules.jsondata import jsondata, enum_options, List, Enum
from src.game.settings import Settings
import src.modules.logger as logger


@jsondata
class Agent:
    id: str

    def __init__(self, i: int):
        self.id = f"agent{i}"
        logger.info(f"Initialized agent {i}")