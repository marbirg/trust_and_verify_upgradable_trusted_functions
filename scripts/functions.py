import sys
from importlib.machinery import SourceFileLoader

from conf_lib import get_config
config = get_config()

print("Using config:", config)

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
    print("libname:", libname)
    print("libpath:", libpath)
    print("module_path:", module_path,flush=True)
    sys.path.append(libpath)
    return SourceFileLoader(libname, module_path).load_module()

def get_dafny_lib(func_name:str):
    print("Get dafny lib",flush=True)
    libname = "dafnylib"
    libpath = get_libpath(func_name)
    return SourceFileLoader(libname, libpath+_DAFNY_MODULE_FILE_NAME).load_module()

def verified_max(a,b):
    func_name = 'Max'
    lib = get_module(func_name)
    Max = lib.default__.Max
    return Max(a,b)
    return 3

def verified_abs(a:int):
    func_name = 'Abs'
    print("Function name:", func_name, flush=True)
    lib = get_module(func_name)
    print("Lib imported", flush=True)
    Abs = lib.default__.Abs
    return Abs(a)

def list_to_dafny_array(Array, l:list):
    arr = Array([],len(l))
    for i in range(len(l)):
        arr[i]=l[i]
    return arr

def dafny_array_to_list(arr):
    lst=list(range(arr.length(0)))
    for i in range(arr.length(0)):
        lst[i]=arr[i]
    return lst

class DafnyArray:
    func_name = 'BubbleSortDafny'
    try:
        dafnylib = get_dafny_lib(func_name)
        Array = dafnylib.Array
    except Exception as e:
        print("Caught exception in DafnyArray:")
        print(e)


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

class DafnyObjArray:
    def __init__(self, libname:str):
        try:
            self.dafnylib = get_dafny_lib(libname)
            self.Array = self.dafnylib.Array
        except Exception as e:
            print("Caught exception in DafnyArray:")
            print(e)

    def list_to_dafny_array(self, l:list):
        arr = self.Array([],len(l))
        for i in range(len(l)):
            arr[i]=l[i]
        return arr

    def dafny_array_to_list(self, arr):
        lst=list(range(arr.length(0)))
        for i in range(arr.length(0)):
            lst[i]=arr[i]
        return lst


def verified_sort(l):
    # func_name = 'BubbleSortDafny'
    func_name = 'Sort'
    lib = get_module(func_name)
    # Sort = lib.default__.BubbleSort
    Sort = lib.default__.Sort
    # arr = DafnyArray.list_to_dafny_array(l)
    dafnyArray = DafnyObjArray(func_name)
    arr = dafnyArray.list_to_dafny_array(l)
    arr = Sort(arr)
    sorted = DafnyArray.dafny_array_to_list(arr)
    return sorted

def verified_count(zone_id:int, zone_count:list[int]):
    func_name = 'Count'
    lib = get_module(func_name)
    Count = lib.default__.Count
    dafnyArray = DafnyObjArray(func_name)
    arr = dafnyArray.list_to_dafny_array(zone_count)
    res = Count(zone_id, arr)
    return res

def verified_voting(votes:list[int]):
    func_name = 'Voting'
    lib = get_module(func_name)
    func = lib.default__.Count__votes
    dafnyArray = DafnyObjArray(func_name)
    arr = dafnyArray.list_to_dafny_array(votes)
    res = func(arr)
    return res

