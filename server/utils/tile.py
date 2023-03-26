from os.path import join, dirname, realpath
import json, re, hashlib
from utils.error_meta import error_meta
from config import PWD

def stable_hash(data):
    m = hashlib.sha256()
    m.update(str(data).encode("utf-8"))
    return m.hexdigest()[:16]

STATE_DIR = join(PWD, 'state')
ASSETS_DIR = join(PWD, 'assets')
TILES_DIR = join(ASSETS_DIR, 'tiles')

class Tile:
    def json(self) -> dict:
        pass

class Tile:
    def __init__(self,
        image, 
        rot,
        i,
        j,
        sides,
        pois,
        cons,
        isStart,
        numShields,
        isGarden,
        isUnplayable
    ):
        self.image = image
        self.rot = rot
        self.i = i
        self.j = j
        self.sides = sides
        self.pois = pois
        self.cons = cons
        self.isStart = isStart
        self.numShields = numShields
        self.isGarden = isGarden
        self.isUnplayable = isUnplayable

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)
    
    def __eq__(self, other: Tile):
        return self.json() == other.json()
    
    def __str__(self):
        return str(self.json())
    
    def __repr__(self):
        return str(self.json())

    def json(self) -> dict:
        return {
            "image": self.image,
            "rot": self.rot,
            "i": self.i,
            "j": self.j,
            "sides": self.sides,
            "pois": self.pois,
            "cons": self.cons,
            "isStart": self.isStart,
            "numShields": self.numShields,
            "isGarden": self.isGarden,
            "isUnplayable": self.isUnplayable 
        }

    def isOnBoard(self) -> bool:
        return self.i is not None and self.j is not None
    
    def isPlayable(self) -> bool:
        return not self.isOnBoard() and not self.isUnplayable

    def file(self) -> str:
        return f"{TILES_DIR}/{self.image}.jpg"
    
    def coors(self) -> dict:
        return {
            "i": self.i,
            "j": self.j
        }

    def rotate_90deg_ccw(self) -> None:
        def mod(n, base):
            return (n - 1) % base + 1
        
        # update rotation
        self.rot = (self.rot + 90) % 360

        # updates sides
        right, top, left, bottom = self.sides["right"], self.sides["top"], self.sides["left"], self.sides["bottom"]
        self.sides["right"], self.sides["top"], self.sides["left"], self.sides["bottom"] = bottom, right, top, left

        # FIXME: update pois

        # Update cons
        self.cons["city"] = [
            [ mod(x + 1, 4) for x in group ]
            for group in self.cons["city"]
        ]
        self.cons["road"] = [
            [ mod(x + 1, 4) for x in group ]
            for group in self.cons["road"]
        ]
        self.cons["field"] = [
            [ mod(x + 2, 8) for x in group ]
            for group in self.cons["field"]
        ]

    def rotate(self, degrees_ccw) -> Tile:
        if degrees_ccw % 90 != 0:
            print(f"Cannot rotate by non-multiple of 90 '{degrees_ccw}'")
            return self
        ccw_rotations = (degrees_ccw % 360) // 90
        for _ in range(ccw_rotations):
            self.rotate_90deg_ccw()
        return self

    @staticmethod
    def load_json(data: dict) -> Tile:
        return Tile(
            image=data["image"], 
            rot=data["rot"],
            i=data["i"],
            j=data["j"],
            sides=data["sides"],
            pois=data["pois"],
            cons=data["cons"],
            isStart=data["isStart"],
            numShields=data["numShields"],
            isGarden=data["isGarden"],
            isUnplayable=data["isUnplayable"]
        )

    @staticmethod
    def parse_num_tiles(s: str):
        # s = basic_v2_CCCC_S_XC1234_N1W
        # pieces = [ CCCC, S, XC1234, N1W ]
        # s = basic_v2_CCCC_S_XC1234_N1W
        # p = [ N1W ]
        # n = 1
        pieces = s.split("_")[2:]
        p = list(filter(lambda p: len(p) > 0 and p[0] == "N", pieces))
        if len(p) != 1:
            return 0
        n = int(re.findall('\d+', p[0][1:])[0])
        return n

    @staticmethod
    def parse_is_start(s: str):
        return "start" in s

    @staticmethod
    def parse_num_shields(s: str):
        return 1 if "_S_" in s else 0

    @staticmethod
    def parse_sides(s: str):
        # s = basic_v2_CCCC_S_XC1234_N1W
        # code = CCCC
        code = s.split("_")[2]
        return {
            "right": code[0],
            "top": code[1],
            "left": code[2],
            "bottom": code[3]
        }

    @staticmethod
    def parse_pois(s: str):
        return []  # FIXME: this needs to be implemented
    
    @staticmethod
    def parse_cons(s: str):
        pieces = s.split("_")
        cons = {
            "city": [],
            "road": [],
            "field": []
        }
        for p in pieces:            
            if p[0] == "X":
                vals = [int(x) for x in p[2:]]
                if p[1] == "C":
                    cons["city"].append(vals)
                elif p[1] == "R":
                    cons["road"].append(vals)
                elif p[1] == "F":
                    cons["field"].append(vals)
        return cons

    @staticmethod
    def load_tiles_from_file(file: str) -> list[dict]:
        try:
            image, ext = file.split(".")
            if ext != "jpg":
                return []

            tiles: list[Tile] = []
            for index in range(Tile.parse_num_tiles(image)):
                isStart = Tile.parse_is_start(image) and index == 0
                tiles.append(Tile(
                    image=image, 
                    rot=0,
                    i=0 if isStart else None,
                    j=0 if isStart else None,
                    sides=Tile.parse_sides(image),
                    pois=Tile.parse_pois(image),
                    cons=Tile.parse_cons(image),
                    isStart=isStart,
                    numShields=Tile.parse_num_shields(image),
                    isGarden=False,
                    isUnplayable=False
                ))
            return tiles
        except Exception as e:
            _, err_func, err_line = error_meta()
            meta = f"{err_func}:{err_line}"
            print(f"Couldn't parse file '{file}'. error: '{e}'. meta={meta}")
            return []
    
    @staticmethod
    def load_tiles() -> list[Tile]:
        tiles = json.load(open(f"{STATE_DIR}/tiles.json", "rb"))
        return [
            Tile.load_json(data)
            for data in tiles
        ]        