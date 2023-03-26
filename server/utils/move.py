# from utils.jsondata import jsondata

# @jsondata
# class Move:
#     i: int
#     j: int
#     rot: int

class Move:
    def json(self) -> dict:
        pass

class Move:
    def __init__(self, i, j, rot):
        self.i = i
        self.j = j
        self.rot = rot

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)
    
    def __eq__(self, other: Move):
        return self.json() == other.json()
    
    def __str__(self):
        return str(self.json())
    
    def __repr__(self):
        return str(self.json())

    def json(self):
        return {
            "i": self.i,
            "j": self.j,
            "rot": self.rot
        }
    
def move_from_json(data) -> Move:
    return Move(
        data["i"],
        data["j"],
        data["rot"]
    )


