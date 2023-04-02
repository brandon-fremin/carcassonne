from src.game.move import Move
from src.game.tile import Tile
from src.game.feature import Feature
from src.game.board import Board
from src.game.transform import Transform
from src.modules.jsondata import dumps, asdict, jsondata
from src.modules.jsondata_implementation.jsondata_encoder import JSONDataEncoder
from src.modules.macros import LINE, FRAME
from src.modules.timer import timer, timer_cb
from enum import Enum


from datetime import datetime

import traceback

import src.modules.logger as logger


def main():
    writers = [
        logger.ColorizedLogWriter(),
        logger.FileLogWriter("output.txt", "w")
    ]
    logger.initialize(writers)
    logger.info("Hello World")

    t = Tile()
    print(repr(t))
    print(asdict(t))
    print(Tile(**asdict(t)))

    class Color(Enum):
        Red: str = "Red"
        Blue: str = "Blue"

    @jsondata
    class Echo:
        color: Color
        x: int

    print(JSONDataEncoder.has_origin(Color))
    print(vars(Color))
    print(Color.__new__)

    e = Echo(color="Red", x="4")
    print(e)
    print(asdict(e))

    @timer_cb(logger.error)
    @timer_cb(logger.warn)
    @timer_cb(logger.info)
    @timer_cb(logger.debug)
    def loop(n: int):
        for _ in range(n):
            pass

    loop(10000000)

    g = {
        "tileId": "x",
        "transform": {
            "rot": 0,
            "i": 1,
            "j": 2
        }
    }

    m = Move("f")
    print(repr(m))

    s = repr(m)
    f = eval(s)
    print(f)

    m = Move()
    print(m)

    print(Move(g))
    print(Move(**g))

    q = {
        "id": 777,
        "image": "b",
        "features": [{
            "id": "a",
            "svg": "",
            "type": "Field",
            "clickableX": 0,
            "clickableY": 1,
            "placeables": [
                {
                    "name": "Meeple",
                    "image": ""
                }
            ]
        }],
        "transform": {
            "rot": 0,
            "i": 1,
            "j": 2
        },
        "sides": {
            "left": "R",
            "right": "R",
            "top": "R",
            "bottom": "R"
        },
        "numShields": 2,
        "isGarden": True
    }
    t = Tile(q)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        tb = traceback.format_exc().strip()
        logger.warn(tb)
        logger.fatal(e)

# m = Move(g)
# n = Move(**g)
# j = Move(m)
# print(m == n == j)
# print(hash(m))
# print(hash(n))
# print(hash(j))
# print(asdict(m))
# print("*******************************************")


# x = {
#     "id": "a",
#     "svg": "",
#     "type": "Field",
#     "clickableX": 0,
#     "clickableY": 1,
#     "placeables": [
#         {
#             "name": "Joe",
#             "image": ""
#         }
#     ]
# }

# X = Feature(x)
# print(X)
# print(vars(X))
# print(dict(X))

# X.hello()

# print(X.__class__)

# print(dumps(X, indent=2))

# print(asdict(X))

# t = Tile(q)

# print(asdict(t))

# x = Tile(asdict(t))

# print(x)

# print(dumps(x.features[0]))


# print(x)
# print(dumps(x, indent=2))

# s = datetime.now().astimezone().isoformat()
