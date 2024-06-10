
import sys
from typing import List, Annotated
from fastapi import FastAPI, Query
import uvicorn
import os
import subprocess
import time
from threading import Thread
from pydantic import BaseModel
# from multiprocessing import Process

from conf_lib import get_config
config = get_config()
# import local_config as local_config
# import enclave_config as enclave_config
# ENV = os.environ.get("ENV")
# print("Environment:", ENV)
# if ENV == 'local':
#     config = local_config
# else:
#     config = enclave_config
# STAGING_DIR = '/data/tmp/'
# DAFNY_OUT = "/data/verified/"
# DAFNY_BIN = "/usr/lib/dafny/dafny"
# DAFNY_TARGET = '/compileTarget:py'

app=FastAPI()
@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/max/{a}/{b}")
def run_max(a:int, b:int):
    from functions import verified_max as Max
    # import sys
    # from importlib.machinery import SourceFileLoader
    # libpath = DAFNY_OUT+'Max' + '-py'
    # sys.path.append(libpath)
    # lib = SourceFileLoader("maxlib", libpath+"/module_.py").load_module()
    # Max = lib.default__.Max
    # res = Max(a,b)
    res = Max(a,b)
    print("Result:", res)

    return res

@app.get("/abs/{a}")
def run_abs(a:int):
    print("Run abs with arg:", a, flush=True)
    from functions import verified_abs as Abs
    print("Function imported", flush=True)
    # import sys
    # from importlib.machinery import SourceFileLoader
    # libpath = DAFNY_OUT+'Abs' + '-py'
    # sys.path.append(libpath)
    # lib = SourceFileLoader("abslib", libpath+"/module_.py").load_module()
    # Abs = lib.default__.Abs
    # return 3
    res = Abs(a)
    print("Result:", res)

    return res

@app.get("/sort/")
def run_sort(l:Annotated[list[int], Query()]):
    from functions import verified_sort as Sort
    sorted = Sort(l)
    print("Initial:", l)
    print("Result:", sorted)
    return sorted

    # import sys
    # from importlib.machinery import SourceFileLoader
    # libpath = DAFNY_OUT+'BubbleSortDafny' + '-py'
    # sys.path.append(libpath)
    # sortlib = SourceFileLoader("sortlib", libpath+"/module_.py").load_module()
    # dafnylib = SourceFileLoader("dafnylib", libpath+"/_dafny.py").load_module()
    # Sort = sortlib.default__.BubbleSort
    # print("List:", l)
    # Array = dafnylib.Array
    # arr = Array([],len(l))
    # for i in range(len(l)):
    #     arr[i]=l[i]
    # print("Init array:",arr)
    # print("Array length:", arr.length(0))
    # print("List length:", len(l))
    # for i in range(arr.length(0)):
    #     print(arr[i], end=" ")
    # print()
    # Sort(arr)
    # print("Sorted array:",arr)
    # sorted = list(range(arr.length(0)))
    # for i in range(arr.length(0)):
    #     print(arr[i], end=" ")
    #     sorted[i]=arr[i]

    # print()

    # # print("dafny array len:", length)
    # print("Result:", sorted)
    # return sorted

class ListItem(BaseModel):
    value: list[int] = [9,0,4,1,5,2,3,6,7,8]

class CodeItem(BaseModel):
    name: str = 'Max'
    body: str = '''if x < y {
  return y;
} else {
  return x;
}
'''
   
@app.post("/sort/")
# def run_sort(l:Annotated[list[int], Query()]):
def run_sort(lstJson:ListItem):
    from functions import verified_sort as Sort
    print(lstJson)
    l = lstJson.value
    sorted = Sort(l)
    print("Initial:", l)
    print("Result:", sorted)
    return sorted

@app.post("/deploy")
async def deploy_code(codeObj:CodeItem):
    print(codeObj, flush=True)
    try:
        create_dafny_file(codeObj.name, codeObj.body)
        path = config.STAGING_DIR + codeObj.name + '.dfy'
        print("Path to verify:", path)
        nerrors = verify_dafny_file(path)
        if nerrors>=0:
            response = codeObj.name + " verified with " + str(nerrors) + " errors"
        else:
            response = "Verification did not succeed"
    except Exception as e:
        response = str(e)
    
    return response

@app.get("/inputs")
async def get_inputs():
    inputs = read_input()
    create_dafny_files(inputs)

    path_list = []
    for fname in inputs:
        fname = replace_suffix(fname,'dfy')
        path_list.append(config.STAGING_DIR + fname)
    # return path_list
    res = verify_all(path_list)
    print("Result:", res)

    # return {"status":200}
    return {"result":res}
    # fname = 'BubbleSortDafny.dfy'
    # path = STAGING_DIR+fname
    # if not os.path.exists(path):
    #     return "File does not exist"

    # res = verify_dafny_file(path)
    # status = 'success' if res else 'fail'
    # # return res
    # # return {'response':"Verification han started"}
    # return 'File ' + fname + ' verified with status:' + str(status)
    # return res
    # return staged
    # # return {"staged": {}}

def verify_all(path_list):
    print(path_list)
    results = []
    for path in path_list:
        print("Verify:", path, flush=True)
        if not os.path.exists(path):
            result_string = "File " + path + " does not exist"
        else:
            nerrors = verify_dafny_file(path)
            status = 'success' if nerrors==0 else 'fail'
            result_string = "File " + path + " verified with status:"+ status
        print(result_string, flush=True)
        results.append(result_string)

    return results


def extract_errors_from_output(output):
    errors = output.split(',')[-1].strip()
    nerrors = errors.split(" ")[0]
    return int(nerrors)

def test_extract_errors_from_output():
    out = "Dafny program verifier finished with 4 verified, 0 errors"
    assert extract_errors_from_output(out)==0

def verify_dafny_file(file_path):
    print("Should verify file:", file_path)
    dafny_file = file_path.split('/')[-1]
    output = config.DAFNY_OUT+dafny_file
    print("File name:", dafny_file)
    command = "{binary} {path} /out:{out} {target}".format(
        binary=config.DAFNY_BIN,
        path=file_path,
        out=output,
        target=config.DAFNY_TARGET
    )
    print("Command:", command)

    try:
        output = subprocess.check_output(['/usr/bin/bash','-c', command])
    except Exception as e:
        print("Caught exception")
        print("Error:",e,flush=True)
        return -1
    print("Dafny output:")
    print(output,flush=True)
    # output = subprocess.run(['/usr/bin/bash','-c', command])
    output=output.decode('utf8')
    print("Output:", output, flush=True)
    expected="Dafny program verifier finished with 1 verified, 0 errors"
    result = output.strip().split('\n')[0]
    nerrors = extract_errors_from_output(result)
    return nerrors
    # return 'done'
    return (result==expected)

    if result==expected:
        print("Verification successfull")
        # print("Move and rename module")
        # src=DAFNY_OUT+libname+'-py'
        # dst=LIB+libname
        # rename_lib(src,dst)
    else:
        print("Verification not successfull")
        print(result)
        print(expected)
        print("---")
   
def read_files_in_dir(dir_path):
    print("Read files from:", dir_path)
    data = {}
    file_names=os.listdir(dir_path)
    for fname in file_names:
        path=dir_path+fname
        with open(path, "r") as f:
            data[fname]=f.read()
        print("-----")
    return data 

# Temporary help function, should be replaced by getting data in web request
def read_input():
    inputs = {}
    # input_dir='/input/'
    input_dir = config.INPUT_DIR
    input_files=os.listdir(input_dir)
    for fname in input_files:
        path=input_dir+fname
        with open(path, "r") as f:
            inputs[fname]=f.read()
        print("-----")
    return inputs 

def read_templates():
    templates = {}
    # template_dir='/templates/'
    template_dir=config.TEMPLATE_DIR
    template_files=os.listdir(template_dir)
    for fname in template_files:
        path=template_dir+fname
        with open(path, "r") as f:
            # print(f.read())
            templates[fname]=f.read()
    return templates

def load_specification(name):
    specification = ""
    template_dir=config.TEMPLATE_DIR
    template_files=os.listdir(template_dir)
    path=template_dir+name
    try:
        with open(path,"r") as f:
            specification=f.read()
        return specification
    except Exception as e:
        print(e)
        return ""

def replace_suffix(string, new_suffix):
    string = string.split('.')
    string[-1]=new_suffix
    return '.'.join(string)

def merge(template, body):
    return template+'\n{\n' + body + '\n}'

def create_dafny_files(inputs):
    templates = read_templates()

    for k in inputs:
        template_name = replace_suffix(k, 'template')
        if template_name in templates:
            dafny_file = merge(templates[template_name], inputs[k])
            dafny_file_name = replace_suffix(k,'dfy')
            path = config.STAGING_DIR+dafny_file_name
            if not os.path.exists(config.STAGING_DIR):
                os.mkdir(config.STAGING_DIR)
            with open(path,'w') as f:
                f.write(dafny_file)
        else:
            print("No corresponding template found")
        print("---")

def create_dafny_file(name:str, body:str):
    specification_name = name+'.template'
    specification = load_specification(specification_name)
    if not specification=="":
        dafny_file = merge(specification,body)
        dafny_file_name = name+'.dfy'
        path = config.STAGING_DIR+dafny_file_name
        if not os.path.exists(config.STAGING_DIR):
            os.mkdir(config.STAGING_DIR)
        with open(path,'w') as f:
            f.write(dafny_file)
            print("Written file",path )
    else:
        print("No corresponding template found")
        raise Exception("No specification with that name found")


    # for k in inputs:
    #     template_name = replace_suffix(k, 'template')
    #     if template_name in templates:
    #         dafny_file = merge(templates[template_name], inputs[k])
    #         dafny_file_name = replace_suffix(k,'dfy')
    #         path = config.STAGING_DIR+dafny_file_name
    #         if not os.path.exists(config.STAGING_DIR):
    #             os.mkdir(config.STAGING_DIR)
    #         with open(path,'w') as f:
    #             f.write(dafny_file)
    #     else:
    #         print("No corresponding template found")
    #     print("---")
from fastapi.responses import HTMLResponse
@app.get("/bandit")
def run_bandit():
    print("Should run bandit")
    binary = 'bandit'
    arg = '-r . -f html'
    report = 'reports/bandit.report.html'
    target = 'scripts' 
    output = f'-o {report}'
    command = f"bandit -r {target} -f html -o {report}"
    # command = f"ls"
    print("Command:", command)

    try:
        output = subprocess.check_output(['/usr/bin/bash','-c', command])

        print("Bandit done")
        print("Output")
    except Exception as e:
        print(str(e))
    # return 200
    with open(report,'r') as f:
        response = f.read()
    print("Response:", response)
    return HTMLResponse(content=response, status_code=200)
    return response

    return output

    return 200

if __name__=='__main__':
    print("Hello world!")
    print(sys.path)
    print("Config settings:")
    print(config)
    print(config.STAGING_DIR)
    print(config.DAFNY_OUT)
    print(config.DAFNY_BIN)
    print(config.DAFNY_TARGET) 

    # uvicorn.run("main:app", loop='asyncio', host='0.0.0.0', port=12341, reload=True)
    
    ENV = os.environ.get("ENV")
    reload = True if ENV=='local' else False
    uvicorn.run("main:app", loop='asyncio', host='0.0.0.0', port=12341, reload=reload)
