
STATIC_COUNTER: int = 0
def make_id():
    global STATIC_COUNTER
    result = str(STATIC_COUNTER)
    STATIC_COUNTER += 1
    return result


class Tile:
    _id: str  # unique string identifier
    _image_name: str  # image file name
    _i: int  # column number (0 is center, positive is right)
    _j: int  # row number (0 is center, positive is up)
    _rotation: int  # counter-clockwise rotation (0, 90, 180, 270)
    _num_shields: int  # number of city shields
    _is_garden: bool  # true if tile has abbot garden

    def __init__(self, id: str, image_name: str, i: int, j: int, rotation: int, num_shields:int, is_garden: bool):
        self._id = id
        self._image_name = image_name
        self._i = i
        self._j = j
        self._rotation = rotation
        self._num_shields = num_shields
        self._is_garden = is_garden

    def id(self) -> str:
        return self._id
    
    def i(self) -> int:
        return self._i
    
    def j(self) -> int:
        return self._j
    
    def image_name(self) -> str:
        return self._image_name

    def rot(self) -> int:
        return self._rotation
    
    def set_i(self, i):
        self._i = int(i)
        return self

    def set_j(self, j):
        self._j = int(j)
        return self

    def set_rot(self, rot):
        self._rotation = int((rot // 90) % 4) * 90 
        return self

class TileA(Tile):
    def __init__(self):
        super().__init__(id=make_id(), image_name="basic_v2_A.jpg", i=None, j=None, rotation=0, num_shields=0, is_garden=False)

class TileB(Tile):
    def __init__(self):
        super().__init__(id=make_id(), image_name="basic_v2_B.jpg", i=None, j=None, rotation=0, num_shields=0, is_garden=False)

class TileC(Tile):
    def __init__(self):
        super().__init__(id=make_id(), image_name="basic_v2_C.jpg", i=None, j=None, rotation=0, num_shields=1, is_garden=False)

class TileD(Tile):
    def __init__(self):
        super().__init__(id=make_id(), image_name="basic_v2_D.jpg", i=None, j=None, rotation=0, num_shields=0, is_garden=False)

class TileE(Tile):
    def __init__(self, is_garden=False):
        super().__init__(id=make_id(), image_name="basic_v2_E.jpg", i=None, j=None, rotation=0, num_shields=0, is_garden=is_garden)
        
class TileF(Tile):
    def __init__(self):
        super().__init__(id=make_id(), image_name="basic_v2_F.jpg", i=None, j=None, rotation=0, num_shields=1, is_garden=False)

class TileG(Tile):
    def __init__(self):
        super().__init__(id=make_id(), image_name="basic_v2_G.jpg", i=None, j=None, rotation=0, num_shields=0, is_garden=False)

class TileH(Tile):
    def __init__(self, is_garden=False):
        super().__init__(id=make_id(), image_name="basic_v2_H.jpg", i=None, j=None, rotation=0, num_shields=0, is_garden=is_garden)

class TileI(Tile):
    def __init__(self, is_garden=False):
        super().__init__(id=make_id(), image_name="basic_v2_I.jpg", i=None, j=None, rotation=0, num_shields=0, is_garden=is_garden)

class TileJ(Tile):
    def __init__(self):
        super().__init__(id=make_id(), image_name="basic_v2_J.jpg", i=None, j=None, rotation=0, num_shields=0, is_garden=False)

class TileK(Tile):
    def __init__(self):
        super().__init__(id=make_id(), image_name="basic_v2_K.jpg", i=None, j=None, rotation=0, num_shields=0, is_garden=False)

class TileL(Tile):
    def __init__(self):
        super().__init__(id=make_id(), image_name="basic_v2_L.jpg", i=None, j=None, rotation=0, num_shields=0, is_garden=False)

class TileM(Tile):
    def __init__(self, is_garden=False):
        super().__init__(id=make_id(), image_name="basic_v2_M.jpg", i=None, j=None, rotation=0, num_shields=1, is_garden=is_garden)

class TileN(Tile):
    def __init__(self, is_garden=False):
        super().__init__(id=make_id(), image_name="basic_v2_N.jpg", i=None, j=None, rotation=0, num_shields=0, is_garden=is_garden)

class TileO(Tile):
    def __init__(self):
        super().__init__(id=make_id(), image_name="basic_v2_O.jpg", i=None, j=None, rotation=0, num_shields=1, is_garden=False)

class TileP(Tile):
    def __init__(self):
        super().__init__(id=make_id(), image_name="basic_v2_P.jpg", i=None, j=None, rotation=0, num_shields=0, is_garden=False)

class TileQ(Tile):
    def __init__(self):
        super().__init__(id=make_id(), image_name="basic_v2_Q.jpg", i=None, j=None, rotation=0, num_shields=1, is_garden=False)

class TileR(Tile):
    def __init__(self, is_garden=False):
        super().__init__(id=make_id(), image_name="basic_v2_R.jpg", i=None, j=None, rotation=0, num_shields=0, is_garden=is_garden)

class TileS(Tile):
    def __init__(self):
        super().__init__(id=make_id(), image_name="basic_v2_S.jpg", i=None, j=None, rotation=0, num_shields=1, is_garden=False)

class TileT(Tile):
    def __init__(self):
        super().__init__(id=make_id(), image_name="basic_v2_T.jpg", i=None, j=None, rotation=0, num_shields=0, is_garden=False)

class TileU(Tile):
    def __init__(self, is_garden=False):
        super().__init__(id=make_id(), image_name="basic_v2_U.jpg", i=None, j=None, rotation=0, num_shields=0, is_garden=is_garden)

class TileV(Tile):
    def __init__(self, is_garden=False):
        super().__init__(id=make_id(), image_name="basic_v2_V.jpg", i=None, j=None, rotation=0, num_shields=0, is_garden=is_garden)

class TileW(Tile):
    def __init__(self):
        super().__init__(id=make_id(), image_name="basic_v2_W.jpg", i=None, j=None, rotation=0, num_shields=0, is_garden=False)

class TileX(Tile):
    def __init__(self):
        super().__init__(id=make_id(), image_name="basic_v2_X.jpg", i=None, j=None, rotation=0, num_shields=0, is_garden=False)
