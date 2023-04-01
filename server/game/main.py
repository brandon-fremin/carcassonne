from move import Move
from tile import Tile
from feature import Feature
from board import Board
from jsondata import dumps, asdict

g = {
    "tileId": "x",
    "transform": {
        "rot": 0,
        "i": 1,
        "j": 2
    }
}

m = Move(g)
n = Move(**g)
j = Move(m)
print(m == n == j)
print(hash(m))
print(hash(n))
print(hash(j))
print(asdict(m))
print("*******************************************")

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
        "left": "c",
        "right": "d",
        "top": "e",
        "bottom": "f"
    },
    "numShields": 2,
    "isGarden": True
}

x = {
    "id": "a",
    "svg": "",
    "type": "Field",
    "clickableX": 0,
    "clickableY": 1,
    "placeables": [
        {
            "name": "Joe",
            "image": ""
        }
    ]
}

X = Feature(x)
print(X)
print(vars(X))
print(dict(X))

X.hello()

print(X.__class__)

print(dumps(X, indent=2))

print(asdict(X))

t = Tile(q)

print(asdict(t))

x = Tile(asdict(t))

print(x)

print(dumps(x.features[0]))


print(x)
print(dumps(x, indent=2))