import sys
from importlib.machinery import SourceFileLoader

from conf_lib import get_config
config = get_config()

_LIB_SUFFIX = 'lib'
_MODULE_FILE_NAME = '/module_.py'
_DAFNY_MODULE_FILE_NAME = '/_dafny.py'

def generate_libname(func_name:str):
    return func_name.lower()+_LIB_SUFFIX

def get_libpath(func_name):
    return config.DAFNY_OUT+func_name + config.DAFNY_PYTHON_SUFFIX

def get_module_path(libpath):
    return libpath+_MODULE_FILE_NAME

def get_libdata(func_name):
    libname = generate_libname(func_name)
    libpath = get_libpath(func_name)
    module_path = get_module_path(libpath) 
    return libname, libpath, module_path

def get_module(func_name:str):
    libname, libpath, module_path = get_libdata(func_name)
    sys.path.append(libpath)
    return SourceFileLoader(libname, module_path).load_module()

def get_dafny_lib(func_name:str):
    libname = "dafnylib"
    libpath = get_libpath(func_name)
    return SourceFileLoader(libname, libpath+_DAFNY_MODULE_FILE_NAME).load_module()

def verified_max(a,b):
    func_name = 'Max'
    lib = get_module(func_name)
    Max = lib.default__.Max
    return Max(a,b)

def verified_abs(a:int):
    func_name = 'Abs'
    lib = get_module(func_name)
    Abs = lib.default__.Abs
    return Abs(a)

class DafnyArray:
    func_name = 'BubbleSortDafny'
    dafnylib = get_dafny_lib(func_name)
    Array = dafnylib.Array

    @staticmethod
    def list_to_dafny_array(l:list):
        arr = DafnyArray.Array([],len(l))
        for i in range(len(l)):
            arr[i]=l[i]
        return arr

    def dafny_array_to_list(arr):
        lst=list(range(arr.length(0)))
        for i in range(arr.length(0)):
            lst[i]=arr[i]
        return lst

def verified_sort(l):
    func_name = 'BubbleSortDafny'
    lib = get_module(func_name)
    Sort = lib.default__.BubbleSort
    arr = DafnyArray.list_to_dafny_array(l)
    Sort(arr)
    sorted = DafnyArray.dafny_array_to_list(arr)
    return sorted
