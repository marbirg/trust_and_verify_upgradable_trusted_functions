import sys
from typing import Callable, Any, TypeVar, NamedTuple
from math import floor
from itertools import count

import module_
import _dafny
import System_

# Module: module_

class default__:
    def  __init__(self):
        pass

    @staticmethod
    def Max(x, y):
        z: int = int(0)
        if (x) < (y):
            z = y
            return z
        elif True:
            z = x
            return z
        return z

