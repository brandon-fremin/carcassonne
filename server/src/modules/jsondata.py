# DO NOT REMOVE IMPORTS, they forward to other modules!
from src.modules.jsondata_implementation.jsondata_init import jsondata__init__factory
import src.modules.jsondata_implementation.jsondata_helper as jsondata_helper
from src.modules.jsondata_implementation.jsondata_encoder import dumps, asdict, JSONDataEncoder
from enum import Enum
from typing import List, Dict, Union, Optional


enum_options = JSONDataEncoder.enum_options


def jsondata(CLASS):
    CLASS.__init__ = jsondata__init__factory(CLASS)
    CLASS.__str__ = jsondata_helper.jsondata__str__
    CLASS.__repr__ = jsondata_helper.jsondata__repr__
    CLASS.__iter__ = jsondata_helper.jsondata__iter__
    CLASS.__eq__ = jsondata_helper.jsondata__eq__
    CLASS.__hash__ = jsondata_helper.jsondata__hash__
    CLASS.__jsondata__ = True  # Mark as JSON data class
    return CLASS
