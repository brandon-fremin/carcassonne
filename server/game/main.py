from move import Move
from tile import Tile
from feature import Feature

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
print(m.asdict())
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
# print(json.dumps(X))
# print(list(X.keys()))
# print(list(X.values()))

X.hello()

print(X.__class__)

print(X.dumps(indent=2))

print(X.asdict())

t = Tile(q)

print(t.asdict())

x = Tile(t.asdict())

print(x)

print(x.features[0].dumps())
