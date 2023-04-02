import copy
from datetime import datetime
from src.modules.jsondata_implementation.jsondata_encoder import JSONDataEncoder, asdict
from typing import Union, Optional


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
    if cls is datetime and type(arg) is str:
        return datetime.fromisoformat(arg)
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


def jsondata__init__(self, *args, **kwargs):
    try:
        kwargs = extract_kwargs(self, *args, **kwargs)
        for field, type_hint in self.__annotations__.items():
            value = (recursive_parse_args(kwargs[field], type_hint)
                     if len(kwargs) > 0
                     else default(type_hint))
            self.__setattr__(field, value)
    except Exception as e:
        raise Exception(f"Error initializing {self.__class__} -> {str(e)}")
    

def jsondata__init__factory(CLASS):
    # If no constructor is explicitly defined, use jsondata contructor
    if CLASS.__init__ == object.__init__:
        return jsondata__init__

    # Try class constructor, failover to jsondata constructor
    original__init__ = CLASS.__init__  # store reference to orignal implementation
    def __init__wrapper(self, *args, **kwargs):
        try:
            original__init__(self, *args, **kwargs)
        except TypeError:
            jsondata__init__(self, *args, **kwargs)
    return __init__wrapper
        