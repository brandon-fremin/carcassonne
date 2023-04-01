import json
import copy
import hashlib
from typing import Union, Optional


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
            return data
        return super().default(obj)


def dumps(obj, **kwargs) -> str:
    return json.dumps(obj, cls=JSONDataEncoder, **kwargs)


def asdict(obj) -> dict:
    return json.loads(dumps(obj))


def extract_kwargs(obj, *args, **kwargs):
    if len(args) == len(kwargs) == 0:
        return {}

    if len(args) != 0 and len(kwargs) != 0:
        raise Exception(
            f"Cannot have both args and kwargs!"
            f" args={args} kwargs={kwargs}")

    if len(args) > 1:  # len(kwargs) == 0
        raise Exception(
            f"Cannot have multiple positional args!"
            f" args={args}")

    if len(args) == 1:  # len(kwargs) == 0
        kwargs = args[0]

    if type(kwargs) is type(obj):  # kwargs was actually a jsondata object
        kwargs = asdict(kwargs)

    if type(kwargs) is not dict:
        raise Exception(
            f"kwargs must be of type dict, not {type(kwargs).__name__}! kwargs={kwargs}")

    extra_keys = list(set(kwargs.keys()).difference(
        set(obj.__annotations__.keys())))
    if len(extra_keys) > 0:
        raise Exception(
            f"kwargs must only have keys in class!"
            f" kwargs={kwargs} annotation={obj.__annotations__} extra_keys={extra_keys}")

    return copy.deepcopy(kwargs)


def parse_list_arg(arg, type_hint):
    if type(arg) is not list:
        raise Exception(f"arg must by a list! arg={arg}")
    new_type_hint = type_hint.__args__[0]
    return [
        recursive_parse_args(new_arg, new_type_hint)
        for new_arg in arg
    ]


def parse_dict_arg(arg, type_hint):
    if type(arg) is not dict:
        raise Exception(f"arg must by a dict! arg={arg}")
    key_cls = type_hint.__args__[0]
    if key_cls is not str:
        raise Exception(
            f"Only str type Dict keys are supported! key_cls={key_cls.__name__}")
    new_type_hint = type_hint.__args__[1]
    return {
        key_cls(k): recursive_parse_args(new_arg, new_type_hint)
        for k, new_arg in arg.items()
    }


def parse_union_arg(arg, type_hint):
    if type(arg) is not dict or len(arg.keys()) != 1:
        raise Exception(
            f"union arg must be a dictionary with exactly one key! arg={arg}")

    union_key = list(arg.keys())[0]
    new_arg = arg[union_key]
    options = type_hint.__args__
    for option in options:
        option_name = JSONDataEncoder.get_union_key(option)
        if union_key.lower() == option_name.lower():
            new_type_hint = option
            return recursive_parse_args(new_arg, new_type_hint)

    raise Exception(
        f"Could not parse arg={arg} as any of options={options}")


def parse_optional_arg(arg, type_hint):
    raise Exception("Not Implemented")


def parse_arg(arg, type_hint):
    cls = type_hint
    return cls(arg)


def recursive_parse_args(arg, type_hint):
    if "__origin__" in dir(type_hint):
        origin = type_hint.__origin__
        if origin is list:
            return parse_list_arg(arg, type_hint)
        elif origin is dict:
            return parse_dict_arg(arg, type_hint)
        elif origin is Union:
            return parse_union_arg(arg, type_hint)
        elif origin is Optional:
            return parse_optional_arg(arg, type_hint)
        else:
            raise Exception(
                f"Cannot parse arg={arg} with type_origin={origin}")
    else:
        return parse_arg(arg, type_hint)


def default(type_hint):
    if "__origin__" in dir(type_hint):
        origin = type_hint.__origin__
        if origin is list:
            return []
        elif origin is dict:
            return {}
        elif origin is Union:
            return None
        elif origin is Optional:
            return None
        else:
            raise Exception(
                f"Cannot parse type_origin={origin} as default")
    else:
        return type_hint()


def impl__init__(self, *args, **kwargs):
    try:
        kwargs = extract_kwargs(self, *args, **kwargs)
        for field, type_hint in self.__annotations__.items():
            value = (recursive_parse_args(kwargs[field], type_hint)
                     if len(kwargs) > 0
                     else default(type_hint))
            self.__setattr__(field, value)
    except Exception as e:
        raise Exception(f"Error initializing {self.__class__} -> {str(e)}")


def impl__repr__(self):
    kw = [f"{k}={v!r}" for k, v in iter(self)]
    kw_str = ", ".join(kw)
    return f"{type(self).__name__}({kw_str})"


def impl__iter__(self):
    keys = self.__annotations__.keys()
    for key in keys:
        value = self.__dict__[key]
        yield key, value


def impl__eq__(self, other):
    return all([
        self.__dict__[k] == other.__dict__[k]
        for k, _ in iter(self)
    ])


def impl__hash__(self):
    m = hashlib.sha256()
    m.update(dumps(self).encode())
    return int(m.hexdigest(), 16)


def jsondata(CLASS):
    CLASS.__init__ = impl__init__
    CLASS.__repr__ = impl__repr__
    CLASS.__iter__ = impl__iter__
    CLASS.__eq__ = impl__eq__
    CLASS.__hash__ = impl__hash__
    return CLASS
