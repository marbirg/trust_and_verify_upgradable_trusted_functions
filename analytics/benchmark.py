
import sys
import config
import requests
import random
import time
import json
import statistics

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Potential files:
# AssertivePrograming_tmp_tmpwf43uz0e_MergeSort.dfy
# BinarySearchTree_tmp_tmp_bn2twp5_bst4copy.dfy
# CS494-final-project_tmp_tmp7nof55uq_bubblesort.dfy
# CVS-Projto1_tmp_tmpb1o0bu8z_searchSort.dfy
# Clover_binary_search.dfy
# Clover_count_lessthan.dfy
# Clover_find.dfy
# Dafny-Exercises_tmp_tmpjm75muf__Session7Exercises_ExerciseBinarySearch.dfy
# Dafny-Exercises_tmp_tmpjm75muf__Session7Exercises_ExerciseBubbleSort.dfy
# Dafny-demo_tmp_tmpkgr_dvdi_Dafny_BinarySearch.dfy
# Dafny_Verify_tmp_tmphq7j0row_Fine_Tune_Examples_50_examples_BinarySearch.dfy


# Ideas
# Sum
# Dafny_Verify_tmp_tmphq7j0row_Fine_Tune_Examples_50_examples_SumArray.dfy

objects = [
    {
        'file':'./run_examples/AssertivePrograming_tmp_tmpwf43uz0e_MergeSort.dfy',
        'lib': 'mergesort',
        'func': 'MergeSort',
        'args': ['list']
     },
    {
        'file':'./run_examples/Dafny-demo_tmp_tmpkgr_dvdi_Dafny_BinarySearch.dfy',
        'lib': 'binsearch',
        'func': 'BinarySearch',
        'args': ['sortedlist', 'entry']
    },
    {
        'file':'./run_examples/Clover_bubble_sort.dfy',
        'lib': 'bubblesort',
        'func': 'BubbleSort',
        'args': ['list']
    },
    {
'file':'./run_examples/Program-Verification-Dataset_tmp_tmpgbdrlnu__Dafny_vampire_project_original_Searching.dfy',
        'lib': 'linsearch',
        'func': 'Find',
        'args': ['list', 'entry']
    },
    {
'file':'./run_examples/Dafny_Verify_tmp_tmphq7j0row_Fine_Tune_Examples_50_examples_SumArray.dfy',
        'lib': 'sum',
        'func': 'SumArray',
        'args': ['list']
    },
]
def hello():
    url = config.host+'/compile'
    res = requests.post(url, json={'body':'my test data', 'name':'some name'}, verify=False)
    print(res.text)

def get_version():
    url = config.host+'/version'
    res = requests.get(url, verify=False)
    return json.loads(res.text)


def compile(obj):
    url = config.host+'/compile'
    with open(obj['file'],'r') as f:
        body = f.read()
    res = requests.post(url, json={'body':body, 'name':obj['lib']}, verify=False)
    return res


def rand_int_array(n:int):
    arr = []
    for i in range(n):
        arr.append(random.randint(0, 1000))
    return arr
def create_args(arg_def):
    args = []
    n=1000
    # n=3
    for spec in arg_def:
        if spec=='list':
            # args.append(random.sample(range(0, 1000), n))
            args.append(rand_int_array(n))
        elif spec=='sortedlist':
            lst = rand_int_array(n)
            lst.sort()
            args.append(lst)
        elif spec=='entry':
            lst = args[-1]
            args.append(random.choice(lst))
    
    return args
def run(func):
    url = config.host+'/run'
    n=1000
    n=3
    args = create_args(func['args'])
    # print("Args:",args)
    # args[0].sort()
    # print("Sorted:", args)
    # exit(0)
    # data = random.sample(range(0, 1000), n)
    body = {
        'func':func['func'],
        'lib':func['lib'],
        'data': args
    }
    start = time.time()
    res = requests.post(url, json=body, verify=False)
    total_time = time.time()-start
    # print(res)
    # print("Result:", res.text)
    # print("Total time:", elapsed)
    # response = json.loads(res.text)
    # print(res.text)
    # elapsed = response['time']
    return res, total_time, args

def write_report_data(report_file_name, report_data):
    with open(report_file_name, 'w+') as f:
        f.write(json.dumps(report_data))


def run_benchmark(iterations=1, report_prefix:str=''):
    result = {}
    for i in range(len(objects)):
        obj = objects[i]
        print("Compile",obj['func'])
        res = compile(obj)
        if res.ok:
            print('Run', obj['func'])
            comp_time = []
            for it in range(iterations):
                res, total_time, args = run(obj)
                if not res.ok:
                    print("Error")
                    exit(0)
                response = json.loads(res.text)
                elapsed_time = response['time']
                comp_time.append(elapsed_time)
                
        result[obj['func']] = comp_time
    # print(result) 
    report_name = report_prefix+'-benchmark.json'
    write_report_data(report_name, result)
    for i in range(len(objects)):
        func = objects[i]['func']
        # print(sum(result[func])/len(result[func]))
        print(func, 'mean:', statistics.mean(result[func]))

if __name__=='__main__':
    # print(sys.argv)
    # if len(sys.argv)>1:
    #     print("Benchmarking:", sys.argv[1])
    # else:
    #     print("Must provide simulation type as argument")
    #     exit(0)
    version = get_version()['version']
    print("Version:", version)
    run_benchmark(iterations=1000, report_prefix=version)
    # index=4
    # compile(objects[index])
    # res, total_time, args = run(objects[index])
    # print(res.text)
    # print("Expected:", sum(args[0]))
    # i = json.loads(res.text)['result']
    # print(i)
    # lst, entry = args
    # print('Entry:', entry)
    # print('Found:', lst[i])

# Non-enclave
# MergeSort mean: 0.033406689643859865
# BinarySearch mean: 0.0018324227333068848
# BubbleSort mean: 0.5650958454608918
# Find mean: 0.001987902641296387
# SumArray mean: 0.002272313594818115

# Version: enclave
# MergeSort mean: 0.05083907961845398
# BinarySearch mean: 0.002819211006164551
# BubbleSort mean: 0.8339147603511811
# Find mean: 0.0030446529388427736
# SumArray mean: 0.0035234429836273192
