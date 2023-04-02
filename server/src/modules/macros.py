from inspect import stack, FrameInfo
import os


######################################################################
# Macro depth is measured relative to the invocation of the macro!!! #
######################################################################


def FRAME(depth: int = 0) -> FrameInfo:
    if type(depth) is not int or depth < 0:
        raise Exception(
            f"FRAME(depth={repr(depth)}) is invalid. "
            f"depth must be a non-negative integer!")
    return stack()[depth + 1]


def LINE(depth: int = 0) -> int:
    return FRAME(depth + 1).lineno


def FILE(depth: int = 0, basename: bool = False) -> int:
    filename = FRAME(depth + 1).filename
    if basename:
        return os.path.basename(filename)
    else:
        return filename


def FUNC(depth: int = 0) -> int:
    return FRAME(depth + 1).function
