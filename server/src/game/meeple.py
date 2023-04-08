from src.modules.jsondata import jsondata, Enum, enum_options


class MeepleType(Enum):
    Meeple: str = "Meeple"
    Abbot: str = "Abbot"


@jsondata
class Meeple:
    name: MeepleType
    image: str

    def __init__(self, *args, **kwargs):
        if len(args) == len(kwargs) == 0:
            self.__init__(MeepleType.Meeple)
        elif len(args) == 1 and len(kwargs) == 0:
            assert args[0] in enum_options(MeepleType)
            self.name = args[0]
            self.image = "TBD"