import json
from typing import Union
from datetime import datetime


class JSONDataEncoder(json.JSONEncoder):
    @staticmethod
    def is_union_type(type_hint):
        return ("__origin__" in dir(type_hint) and type_hint.__origin__ is Union)

    @staticmethod
    def get_union_key(data_field):
        union_key = data_field.__name__
        return union_key[0].lower() + union_key[1:]

    def default(self, obj):
        if "__iter__" in dir(obj) and "__annotations__" in dir(obj):
            data = dict(obj)
            for field, type_hint in obj.__annotations__.items():
                if JSONDataEncoder.is_union_type(type_hint):
                    union_key = JSONDataEncoder.get_union_key(
                        type(data[field]))
                    data[field] = {union_key: data[field]}
                elif type_hint is datetime:
                    data[field] = data[field].isoformat()
            return data
        return super().default(obj)


def dumps(obj, **kwargs) -> str:
    return json.dumps(obj, cls=JSONDataEncoder, **kwargs)


def asdict(obj) -> dict:
    return json.loads(dumps(obj))
