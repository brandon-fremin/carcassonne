from src.modules.jsondata import jsondata, List, enum_options
from functools import cache
from src.game.tile import Tile
from src.game.feature import Feature, FeatureType, Conn, Coordinate
from src.game.types import Side
import src.modules.logger as logger


def basicV2(code):
    return f"basic_v2_{code}"


def monastery() -> Feature:
    feature = Feature()
    feature.type = FeatureType.Monastary
    feature.clickable.x = feature.clickable.y = 50
    return feature


def field() -> Feature:
    feature = Feature()
    feature.type = FeatureType.Field
    return feature


def right_city() -> Feature:
    feature = Feature()
    feature.type = FeatureType.City
    feature.clickable.x = 85
    feature.clickable.y = 50
    feature.connections = [Conn.RB, Conn.RM, Conn.RT]
    return feature


def top_city() -> Feature:
    feature = Feature()
    feature.type = FeatureType.City
    feature.clickable.x = 50
    feature.clickable.y = 85
    feature.connections = [Conn.TR, Conn.TM, Conn.TL]
    return feature


def left_city() -> Feature:
    feature = Feature()
    feature.type = FeatureType.City
    feature.clickable.x = 15
    feature.clickable.y = 50
    feature.connections = [Conn.LT, Conn.LM, Conn.LB]
    return feature


def bottom_city() -> Feature:
    feature = Feature()
    feature.type = FeatureType.City
    feature.clickable.x = 50
    feature.clickable.y = 15
    feature.connections = [Conn.BL, Conn.BM, Conn.BR]
    return feature


def right_road() -> Feature:
    feature = Feature()
    feature.type = FeatureType.Road
    feature.clickable.x = 75
    feature.clickable.y = 50
    feature.connections = [Conn.RM]
    return feature


def top_road() -> Feature:
    feature = Feature()
    feature.type = FeatureType.Road
    feature.clickable.x = 50
    feature.clickable.y = 75
    feature.connections = [Conn.TM]
    return feature


def left_road() -> Feature:
    feature = Feature()
    feature.type = FeatureType.Road
    feature.clickable.x = 25
    feature.clickable.y = 50
    feature.connections = [Conn.LM]
    return feature


def bottom_road() -> Feature:
    feature = Feature()
    feature.type = FeatureType.Road
    feature.clickable.x = 50
    feature.clickable.y = 25
    feature.connections = [Conn.BM]
    return feature


def group_features(*args) -> Feature:
    features: List[Feature] = args
    for feature in features:
        assert feature.type == features[0].type
    res = Feature(features[0])
    res.clickable.x = sum([f.clickable.x for f in features]) // len(features)
    res.clickable.y = sum([f.clickable.y for f in features]) // len(features)
    res.connections = []
    for f in features:
        res.connections.extend(f.connections)
    return res


def right_top_road() -> Feature:
    return group_features(right_road(), top_road())


def top_left_road() -> Feature:
    return group_features(top_road(), left_road())


def left_bottom_road() -> Feature:
    return group_features(left_road(), bottom_road())


def bottom_right_road() -> Feature:
    return group_features(bottom_road(), right_road())


def left_right_road() -> Feature:
    return group_features(left_road(), right_road())


def top_bottom_road() -> Feature:
    return group_features(top_road(), bottom_road())


def right_top_city() -> Feature:
    return group_features(right_city(), top_city())


def top_left_city() -> Feature:
    return group_features(top_city(), left_city())


def left_bottom_city() -> Feature:
    return group_features(left_city(), bottom_city())


def bottom_right_city() -> Feature:
    return group_features(bottom_city(), right_city())


def left_right_city() -> Feature:
    return group_features(left_city(), right_city())


def top_bottom_city() -> Feature:
    return group_features(top_city(), bottom_city())


def right_top_left_city() -> Feature:
    return group_features(right_city(), top_city(), left_city())


def top_left_bottom_city() -> Feature:
    return group_features(top_city(), left_city(), bottom_city())


def left_bottom_right_city() -> Feature:
    return group_features(left_city(), bottom_city(), right_city())


def bottom_right_top_city() -> Feature:
    return group_features(bottom_city(), right_city(), top_city())


def right_top_left_bottom_city() -> Feature:
    return group_features(right_city(), top_city(), left_city(), bottom_city())


@cache
def tile_manifest() -> List[Tile]:
    ##########################################################################
    # TILE_A #################################################################
    ##########################################################################
    TILE_A = Tile()
    TILE_A.image = basicV2("A")
    TILE_A.sides.left = TILE_A.sides.right = TILE_A.sides.top = Side.Field
    TILE_A.sides.bottom = Side.Road
    TILE_A.features.append(monastery())
    TILE_A.features.append(bottom_road())

    feature = field()
    feature.clickable.x = 75
    feature.clickable.y = 75
    feature.connections = [Conn.RM, Conn.RT, Conn.TR, Conn.TM,
                        Conn.TL, Conn.LT, Conn.LM, Conn.LB, Conn.BL, Conn.BR, Conn.RB]
    TILE_A.features.append(feature)


    ##########################################################################
    # TILE_B #################################################################
    ##########################################################################
    TILE_B = Tile()
    TILE_B.image = basicV2("B")
    TILE_B.sides.left = TILE_B.sides.right = TILE_B.sides.top = TILE_B.sides.bottom = Side.Field
    TILE_B.features.append(monastery())

    feature = field()
    feature.clickable.x = 75
    feature.clickable.y = 75
    feature.connections = [Conn.RM, Conn.RT, Conn.TR, Conn.TM,
                        Conn.TL, Conn.LT, Conn.LM, Conn.LB, Conn.BL, Conn.BM, Conn.BR, Conn.RB]
    TILE_B.features.append(feature)


    ##########################################################################
    # TILE_C #################################################################
    ##########################################################################
    TILE_C = Tile()
    TILE_C.image = basicV2("C")
    TILE_C.sides.left = TILE_C.sides.right = TILE_C.sides.top = TILE_C.sides.bottom = Side.City
    TILE_C.features.append(right_top_left_bottom_city())


    ##########################################################################
    # TILE_D #################################################################
    ##########################################################################
    TILE_D = Tile()
    TILE_D.image = basicV2("D")
    TILE_D.sides.top = Side.City
    TILE_D.sides.left = TILE_D.sides.right = Side.Road
    TILE_D.sides.bottom = Side.Field
    TILE_D.features.append(top_city())
    TILE_D.features.append(left_right_road())

    feature = field()
    feature.clickable.x = 50
    feature.clickable.y = 60
    feature.connections = [Conn.RT, Conn.LT]
    TILE_D.features.append(feature)

    feature = field()
    feature.clickable.x = 50
    feature.clickable.y = 40
    feature.connections = [Conn.RB, Conn.BL, Conn.BM, Conn.BR, Conn.LB]
    TILE_D.features.append(feature)


    ##########################################################################
    # TILE_E #################################################################
    ##########################################################################
    TILE_E = Tile()
    TILE_E.image = basicV2("E")
    TILE_E.sides.top = Side.City
    TILE_E.sides.left = TILE_E.sides.right = TILE_E.sides.bottom = Side.Field
    TILE_E.features.append(top_city())

    feature = field()
    feature.clickable.x = 50
    feature.clickable.y = 50
    feature.connections = [Conn.RM, Conn.RT, Conn.LT,
                        Conn.LM, Conn.LB, Conn.BL, Conn.BM, Conn.BR, Conn.RB]
    TILE_E.features.append(feature)


    ##########################################################################
    # TILE_F #################################################################
    ##########################################################################
    TILE_F = Tile()
    TILE_F.image = basicV2("F")
    TILE_F.sides.left = TILE_F.sides.right = Side.City
    TILE_F.sides.top = TILE_F.sides.bottom = Side.Field
    TILE_F.numShields = 1
    TILE_F.features.append(left_right_city())

    feature = field()
    feature.clickable.x = 50
    feature.clickable.y = 85
    feature.connections = [Conn.TR, Conn.TM, Conn.TL]
    TILE_F.features.append(feature)

    feature = field()
    feature.clickable.x = 50
    feature.clickable.y = 15
    feature.connections = [Conn.BL, Conn.BM, Conn.BR]
    TILE_F.features.append(feature)


    ##########################################################################
    # TILE_G #################################################################
    ##########################################################################
    TILE_G = Tile(TILE_F)
    TILE_F.image = basicV2("G")
    TILE_G.numShields = 0


    ##########################################################################
    # TILE_H #################################################################
    ##########################################################################
    TILE_H = Tile()
    TILE_H.image = basicV2("H")
    TILE_H.sides.left = TILE_H.sides.right = Side.City
    TILE_H.sides.top = TILE_H.sides.bottom = Side.Field
    TILE_H.features.append(right_city())
    TILE_H.features.append(left_city())

    feature = field()
    feature.clickable.x = 50
    feature.clickable.y = 50
    feature.connections = [Conn.TR, Conn.TM, Conn.TL, Conn.BL, Conn.BM, Conn.BR]
    TILE_H.features.append(feature)


    ##########################################################################
    # TILE_I #################################################################
    ##########################################################################
    TILE_I = Tile()
    TILE_I.image = basicV2("I")
    TILE_I.sides.top = TILE_I.sides.right = Side.City
    TILE_I.sides.left = TILE_I.sides.bottom = Side.Field
    TILE_I.features.append(right_city())
    TILE_I.features.append(top_city())

    feature = field()
    feature.clickable.x = 50
    feature.clickable.y = 50
    feature.connections = [Conn.LT, Conn.LM, Conn.LB, Conn.BL, Conn.BM, Conn.BR]
    TILE_I.features.append(feature)


    ##########################################################################
    # TILE_J #################################################################
    ##########################################################################
    TILE_J = Tile()
    TILE_J.image = basicV2("J")
    TILE_J.sides.right = TILE_J.sides.bottom = Side.Road
    TILE_J.sides.left = Side.Field
    TILE_J.sides.top = Side.City
    TILE_J.features.append(top_city())
    TILE_J.features.append(bottom_right_road())

    feature = field()
    feature.clickable.x = 85
    feature.clickable.y = 15
    feature.connections = [Conn.BR, Conn.RB]
    TILE_J.features.append(feature)

    feature = field()
    feature.clickable.x = 15
    feature.clickable.y = 50
    feature.connections = [Conn.RT, Conn.LT, Conn.LM, Conn.LB, Conn.BL]
    TILE_J.features.append(feature)


    ##########################################################################
    # TILE_K #################################################################
    ##########################################################################
    TILE_K = Tile()
    TILE_K.image = basicV2("K")
    TILE_K.sides.left = TILE_K.sides.bottom = Side.Road
    TILE_K.sides.right = Side.Field
    TILE_K.sides.top = Side.City
    TILE_K.features.append(top_city())
    TILE_K.features.append(left_bottom_road())

    feature = field()
    feature.clickable.x = 15
    feature.clickable.y = 15
    feature.connections = [Conn.LB, Conn.BL]
    TILE_K.features.append(feature)

    feature = field()
    feature.clickable.x = 85
    feature.clickable.y = 50
    feature.connections = [Conn.RB, Conn.RM, Conn.RT, Conn.LT, Conn.BR]
    TILE_K.features.append(feature)


    ##########################################################################
    # TILE_L #################################################################
    ##########################################################################
    TILE_L = Tile()
    TILE_L.image = basicV2("L")
    TILE_L.sides.right = TILE_L.sides.bottom = TILE_L.sides.left = Side.Road
    TILE_L.sides.top = Side.City
    TILE_L.features.append(top_city())
    TILE_L.features.append(left_road())
    TILE_L.features.append(bottom_road())
    TILE_L.features.append(right_road())

    feature = field()
    feature.clickable.x = 50
    feature.clickable.y = 60
    feature.connections = [Conn.RT, Conn.LT]
    TILE_L.features.append(feature)

    feature = field()
    feature.clickable.x = 15
    feature.clickable.y = 15
    feature.connections = [Conn.LB, Conn.BL]
    TILE_L.features.append(feature)

    feature = field()
    feature.clickable.x = 85
    feature.clickable.y = 15
    feature.connections = [Conn.BR, Conn.RB]
    TILE_L.features.append(feature)


    ##########################################################################
    # TILE_M #################################################################
    ##########################################################################
    TILE_M = Tile()
    TILE_M.image = basicV2("M")
    TILE_M.sides.right = TILE_M.sides.top = Side.City
    TILE_M.sides.left = TILE_M.sides.bottom = Side.Field
    TILE_M.numShields = 1
    TILE_M.features.append(right_top_city())

    feature = field()
    feature.clickable.x = 15
    feature.clickable.y = 15
    feature.connections = [Conn.LT, Conn.LM, Conn.LB, Conn.BL, Conn.BM, Conn.BR]
    TILE_M.features.append(feature)


    ##########################################################################
    # TILE_N #################################################################
    ##########################################################################
    TILE_N = Tile(TILE_M)
    TILE_M.image = basicV2("N")
    TILE_N.numShields = 0


    ##########################################################################
    # TILE_O #################################################################
    ##########################################################################
    TILE_O = Tile()
    TILE_O.image = basicV2("O")
    TILE_O.sides.right = TILE_O.sides.bottom = Side.Road
    TILE_O.sides.left = TILE_O.sides.top = Side.City
    TILE_O.numShields = 1
    TILE_O.features.append(top_left_city())
    TILE_O.features.append(bottom_right_road())

    feature = field()
    feature.clickable.x = 25
    feature.clickable.y = 15
    feature.connections = [Conn.RT, Conn.BL]
    TILE_O.features.append(feature)

    feature = field()
    feature.clickable.x = 85
    feature.clickable.y = 15
    feature.connections = [Conn.BR, Conn.RB]
    TILE_O.features.append(feature)


    ##########################################################################
    # TILE_P #################################################################
    ##########################################################################
    TILE_P = Tile(TILE_O)
    TILE_P.image = basicV2("P")
    TILE_P.numShields = 0


    ##########################################################################
    # TILE_Q #################################################################
    ##########################################################################
    TILE_Q = Tile()
    TILE_Q.image = basicV2("Q")
    TILE_Q.sides.right = TILE_Q.sides.top = TILE_Q.sides.left = Side.City
    TILE_Q.sides.bottom = Side.Field
    TILE_Q.numShields = 1
    TILE_Q.features.append(right_top_left_city())

    feature = field()
    feature.clickable.x = 50
    feature.clickable.y = 15
    feature.connections = [Conn.BL, Conn.BM, Conn.BR]
    TILE_Q.features.append(feature)


    ##########################################################################
    # TILE_R #################################################################
    ##########################################################################
    TILE_R = Tile(TILE_Q)
    TILE_R.image = basicV2("R")
    TILE_R.numShields = 0


    ##########################################################################
    # TILE_S #################################################################
    ##########################################################################
    TILE_S = Tile()
    TILE_S.image = basicV2("S")
    TILE_S.sides.right = TILE_S.sides.top = TILE_S.sides.left = Side.City
    TILE_S.sides.bottom = Side.Road
    TILE_S.numShields = 1
    TILE_S.features.append(right_top_left_city())
    TILE_S.features.append(bottom_road())

    feature = field()
    feature.clickable.x = 75
    feature.clickable.y = 15
    feature.connections = [Conn.BR]
    TILE_S.features.append(feature)

    feature = field()
    feature.clickable.x = 25
    feature.clickable.y = 15
    feature.connections = [Conn.BL]
    TILE_S.features.append(feature)


    ##########################################################################
    # TILE_T #################################################################
    ##########################################################################
    TILE_T = Tile(TILE_S)
    TILE_T.image = basicV2("T")
    TILE_T.numShields = 0


    ##########################################################################
    # TILE_U #################################################################
    ##########################################################################
    TILE_U = Tile()
    TILE_U.image = basicV2("U")
    TILE_U.sides.top = TILE_U.sides.bottom = Side.Road
    TILE_U.sides.left = TILE_U.sides.right = Side.Field
    TILE_U.features.append(top_bottom_road())

    feature = field()
    feature.clickable.x = 85
    feature.clickable.y = 50
    feature.connections = [Conn.BR, Conn.RB, Conn.RM, Conn.RT, Conn.TR]
    TILE_U.features.append(feature)

    feature = field()
    feature.clickable.x = 15
    feature.clickable.y = 50
    feature.connections = [Conn.TL, Conn.LT, Conn.LM, Conn.LB, Conn.BL]
    TILE_U.features.append(feature)


    ##########################################################################
    # TILE_V #################################################################
    ##########################################################################
    TILE_V = Tile()
    TILE_V.image = basicV2("V")
    TILE_V.sides.left = TILE_V.sides.bottom = Side.Road
    TILE_V.sides.top = TILE_V.sides.right = Side.Field
    TILE_V.features.append(left_bottom_road())

    feature = field()
    feature.clickable.x = 15
    feature.clickable.y = 15
    feature.connections = [Conn.LB, Conn.BL]
    TILE_V.features.append(feature)

    feature = field()
    feature.clickable.x = 85
    feature.clickable.y = 85
    feature.connections = [Conn.BR, Conn.RB, Conn.RM,
                        Conn.RT, Conn.TR, Conn.TM, Conn.TL, Conn.LT]
    TILE_V.features.append(feature)


    ##########################################################################
    # TILE_W #################################################################
    ##########################################################################
    TILE_W = Tile()
    TILE_W.image = basicV2("W")
    TILE_W.sides.left = TILE_W.sides.bottom = TILE_W.sides.right = Side.Road
    TILE_W.sides.top = Side.Field
    TILE_W.features.append(right_road())
    TILE_W.features.append(left_road())
    TILE_W.features.append(bottom_road())

    feature = field()
    feature.clickable.x = 15
    feature.clickable.y = 15
    feature.connections = [Conn.LB, Conn.BL]
    TILE_W.features.append(feature)

    feature = field()
    feature.clickable.x = 85
    feature.clickable.y = 15
    feature.connections = [Conn.BR, Conn.RB]
    TILE_W.features.append(feature)

    feature = field()
    feature.clickable.x = 50
    feature.clickable.y = 75
    feature.connections = [Conn.RT, Conn.TR, Conn.TM, Conn.TL, Conn.LT]
    TILE_W.features.append(feature)


    ##########################################################################
    # TILE_X #################################################################
    ##########################################################################
    TILE_X = Tile()
    TILE_X.image = basicV2("X")
    TILE_X.sides.left = TILE_X.sides.bottom = TILE_X.sides.right = TILE_X.sides.top = Side.Road
    TILE_X.features.append(right_road())
    TILE_X.features.append(left_road())
    TILE_X.features.append(bottom_road())
    TILE_X.features.append(top_road())

    feature = field()
    feature.clickable.x = 15
    feature.clickable.y = 15
    feature.connections = [Conn.LB, Conn.BL]
    TILE_X.features.append(feature)

    feature = field()
    feature.clickable.x = 85
    feature.clickable.y = 15
    feature.connections = [Conn.BR, Conn.RB]
    TILE_X.features.append(feature)

    feature = field()
    feature.clickable.x = 85
    feature.clickable.y = 85
    feature.connections = [Conn.RT, Conn.TR]
    TILE_X.features.append(feature)

    feature = field()
    feature.clickable.x = 15
    feature.clickable.y = 85
    feature.connections = [Conn.TL, Conn.LT]
    TILE_X.features.append(feature)


    manifest = [
        TILE_A,
        TILE_B,
        TILE_C,
        TILE_D,
        TILE_E,
        TILE_F,
        TILE_G,
        TILE_H,
        TILE_I,
        TILE_J,
        TILE_K,
        TILE_L,
        TILE_M,
        TILE_N,
        TILE_O,
        TILE_P,
        TILE_Q,
        TILE_R,
        TILE_S,
        TILE_T,
        TILE_U,
        TILE_V,
        TILE_W,
        TILE_X
    ]

    for tile in manifest:
        # Validate features
        connections = []
        for idx, feature in enumerate(tile.features):
            sides = "_".join([c.name for c in feature.connections])
            feature.id = f"feature{idx}_{feature.type.name}_{sides}"
            connections.extend(feature.connections)
        
        options = enum_options(Conn)
        if (
            len(connections) != len(options) or
            set(connections) != set(options)
        ):
            raise Exception(f"Malformed connections for tile: {tile}")
    
    return manifest


def tile_default_start():
    return tile_manifest()[3]


TILE_DEFAULT_COUNTS = [
    2,
    4,
    1,
    4,
    5,
    2,
    1,
    3,
    2,
    3,
    3,
    3,
    2,
    3,
    2,
    3,
    1,
    3,
    2,
    1,
    8,
    9,
    4,
    1
]


TILE_DEFAULT_GARDENS = [
    0,
    0,
    0,
    0,
    1,
    0,
    0,
    1,
    1,
    0,
    0,
    0,
    1,
    1,
    0,
    0,
    0,
    1,
    0,
    0,
    1,
    1,
    0,
    0
]