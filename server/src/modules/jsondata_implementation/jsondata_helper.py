from src.modules.jsondata_implementation.jsondata_encoder import dumps
from src.modules.hash import sha256


def jsondata__str__(self):
    kw = [f"{k}={v}" for k, v in iter(self)]
    kw_str = ", ".join(kw)
    return f"{type(self).__name__}({kw_str})"


def jsondata__repr__(self):
    kw = [f"{k}={v!r}" for k, v in iter(self)]
    kw_str = ", ".join(kw)
    return f"{type(self).__name__}({kw_str})"


def jsondata__iter__(self):
    keys = self.__annotations__.keys()
    for key in keys:
        value = self.__dict__[key]
        yield key, value


def jsondata__eq__(self, other):
    if type(self) is not type(other):
        return False
    return all([
        self.__dict__[k] == other.__dict__[k]
        for k, _ in iter(self)
    ])


def jsondata__hash__(self):
    hex = sha256(dumps(self))
    return int(hex, 16)