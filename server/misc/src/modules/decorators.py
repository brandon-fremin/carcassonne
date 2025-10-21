from src.modules.macros import FRAME
import src.modules.logger as logger


def protected(func):
    locals = FRAME(1).frame.f_locals
    module = locals.get('__module__', None)
    qualname = locals.get('__qualname__', None)
    # FIXME: This is not sturdy!!
    inferred_class = f"<class '{module}.{qualname}'>"
    inferred_funcname = f"{inferred_class}::{func.__name__}"
    logger.info(f"{inferred_funcname}(...) declared as protected function")

    def wrapper(*args, **kwargs):
        caller_class = FRAME(1).frame.f_locals.get("self", None).__class__
        mro = [str(cls) for cls in caller_class.mro()]
        if inferred_class in mro:
            return func(*args, **kwargs)
        raise Exception(
            f"Call to protected function {inferred_funcname}"
            f" from {caller_class} with mro={mro}")
    return wrapper


def except_with_default(default):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                return default
        return wrapper
    return decorator
