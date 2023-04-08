import json
from typing import List, Dict, Union, Optional, get_origin, get_args
from enum import Enum
from datetime import datetime


def except_with_default(default):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                return default
        return wrapper
    return decorator


class JSONDataEncoder(json.JSONEncoder):
    @staticmethod
    def has_origin(type_hint):
        return "__origin__" in dir(type_hint)

    @staticmethod
    def is_union_type(type_hint):
        return get_origin(type_hint) is Union and type(None) not in get_args(type_hint)

    @staticmethod
    def is_list_type(type_hint):
        return get_origin(type_hint) is list

    @staticmethod
    def is_dict_type(type_hint):
        return get_origin(type_hint) is dict

    @staticmethod
    def is_optional_type(type_hint):
        return get_origin(type_hint) is Union and type(None) in get_args(type_hint)

    @staticmethod
    @except_with_default(False)
    def safe_mro(type_hint, cls):
        return cls in type_hint.mro()

    @staticmethod
    def is_datetime_type(type_hint):
        return JSONDataEncoder.safe_mro(type_hint, datetime)

    @staticmethod
    def is_enum_type(type_hint):
        return JSONDataEncoder.safe_mro(type_hint, Enum)
    
    @staticmethod
    def enum_options(type_hint):
        if not JSONDataEncoder.is_enum_type(type_hint):
            return []
        return list(type_hint._member_map_.values())

    @staticmethod
    def get_union_key(data_field):
        union_key = data_field.__name__
        return union_key[0].lower() + union_key[1:]

    @staticmethod
    def serialize(obj, type_hint):
        if JSONDataEncoder.is_union_type(type_hint):
            union_key = JSONDataEncoder.get_union_key(
                type(obj))
            return {union_key: obj}
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Enum):
            return obj.value
        return obj

    @staticmethod
    def deserialize(obj, type_hint):
        if JSONDataEncoder.is_datetime_type(type_hint) and type(obj) is str:
            return datetime.fromisoformat(obj)
        elif JSONDataEncoder.is_enum_type(type_hint):
            return type_hint(obj)
        return type_hint(obj)

    @staticmethod
    def is_jsondata(obj):
        return "__jsondata__" in dir(obj)

    def default(self, obj):
        if JSONDataEncoder.is_jsondata(obj):
            data = dict(obj)
            for field, type_hint in obj.__annotations__.items():
                data[field] = JSONDataEncoder.serialize(data[field], type_hint)
            return data
        elif isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def dumps(obj, **kwargs) -> str:
    return json.dumps(obj, cls=JSONDataEncoder, **kwargs)


def asdict(obj) -> dict:
    return json.loads(dumps(obj))
