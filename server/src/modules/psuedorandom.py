from src.modules.jsondata import jsondata
from src.modules.hash import sha256
import uuid


@jsondata
class PsuedoRandom():
    seed: str
    iteration: int
    current: str

    def __init__(self, seed) -> None:
        assert type(seed) in [int, str]
        self.seed = seed
        self.iteration = 0
        self.current = seed

    def next(self) -> None:
        self.current = sha256(self.current)
        self.iteration += 1
        return self.current

    def next_int(self) -> None:
        return int(self.next(), 16)

    def choice(self, array):
        n = len(array)
        return array[self.next_int() % n]

    def shuffle(self, array: list) -> list:
        n = len(array)
        for i in range(1, n):
            j = self.next_int() % (i + 1)
            array[i], array[j] = array[j], array[i] 
        return array
    
    @staticmethod
    def uuid() -> str:
        return sha256(uuid.uuid4())
    
    @staticmethod
    def id(length=16) -> str:
        unique_id = sha256(uuid.uuid4())
        if length < len(unique_id):
            unique_id = unique_id[:length]
        return unique_id