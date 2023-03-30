import dataclasses
import json


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


def dumps(obj: dict, **kwargs) -> str:
    return json.dumps(obj, cls=EnhancedJSONEncoder, **kwargs)


def loads(s: str, **kwargs) -> dict:
    return json.loads(s, **kwargs)


def asdict(o) -> dict:
    return dataclasses.asdict(o)
