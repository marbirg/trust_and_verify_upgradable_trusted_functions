
import sys
from typing import List, Annotated
from fastapi import FastAPI, Query
import uvicorn
import os 
import subprocess
import time
from threading import Thread
from pydantic import BaseModel
import ssl
import json

import traceback
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse

from conf_lib import get_config

from taxi_congestion import router as taxi_router

config = get_config()
app=FastAPI()

app.include_router(taxi_router, prefix='/taxi')

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
    
class FuncItem(BaseModel):
    func: str 
    lib: str
    data: list

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/version")
async def get_version():
    if not os.path.exists("/dev/attestation/report"):
        version = 'non-enclave'
    else:
        version = 'enclave'
    return {"version":version}

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

@app.post("/sort/")
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
    res = verify_all(path_list)
    print("Result:", res)

    return {"result":res}

@app.post("/verify")
async def verify_dafny_code(codeObj:CodeItem):
    name = codeObj.name.replace(" ", "_")
    path = config.STAGING_DIR+name
    path = config.STAGING_DIR + 'tmp.dfy'
    print(codeObj.name)
    with open(path, 'w+') as f:
        f.write(codeObj.body)
        
    start = time.time()
    errors = verify_dafny_file(path, compile=False)
    total = time.time()-start
    try:
        os.remove(path)
    except e:
        print("Could not remove files", flush=True)
        print(e)
        print()

    result = {'errors': errors, 'time': total}
    return JSONResponse(content=result)
    
@app.post("/compile")
async def verfy_compile_dafny_code(codeObj:CodeItem):
    name = codeObj.name.replace(" ", "_")
    path = config.STAGING_DIR+name
    if not path.endswith('.dfy'):
        path+='.dfy'
    print("Name:", name)
    print("path:", path)
    # print(codeObj.name)
    if not os.path.exists(config.STAGING_DIR):
        os.mkdir(config.STAGING_DIR)
    with open(path, 'w+') as f:
        f.write(codeObj.body)
        
    # print("Wrote:")
    # print(codeObj.body)
    start = time.time()
    errors = verify_dafny_file(path, compile=True)
    total = time.time()-start
    try:
        os.remove(path)
    except e:
        print("Could not remove files", flush=True)
        print(e)
        print()

    result = {'errors': errors, 'time': total}
    return JSONResponse(content=result)

@app.post("/run")
async def run_dafny_code(funcObj:FuncItem):
    start = time.time()
    from importlib.machinery import SourceFileLoader

    libpath = config.DAFNY_OUT+funcObj.lib + "-py"
    sys.path.append(libpath)

    lib = SourceFileLoader("lib", libpath+"/module_.py").load_module()
    default_class = getattr(lib, "default__")
    my_func = getattr(default_class, funcObj.func)

    from functions import list_to_dafny_array, dafny_array_to_list
    dafnylib = SourceFileLoader("dafnylib", libpath+"/_dafny.py").load_module()
    Array = getattr(dafnylib, "Array")

    # print("Data:", funcObj.data)

    args = []
    for arg in funcObj.data:
        # print("arg:", arg)
        if isinstance(arg, list):
            data_array = list_to_dafny_array(Array, arg)
            args.append(data_array)
        else:
            args.append(arg)

    args = tuple(args)
    # print("Args:", args)
    result = my_func(*args) 
    if not result:
        result = args

    elapsed = time.time()-start
    print("Result:", result)
    return {'result':result, 'time':elapsed}
    return 200
    sorted_lst = dafny_array_to_list(sorted_arr)

    print(my_class)
    print(my_func)
    print(sorted_arr)
    print(sorted_lst)

    # mod = loader.load_module()
    # print(mod)
    # Sort = sortlib.default__.BubbleSort
    # from importlib.abc import Loader
    # func = lib.default__.MergeSort
    # print(lib)
    # funcname = 'MergeSort'
    # print(globals()[funcname])
    # print(globals())

    # import importlib
    # importlib.import_module(libpath+"/module_.py", package=None)

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
    # print('error output:', output)
    errors = output.split(',')[-1].strip()
    nerrors = errors.split(" ")[0]
    return int(nerrors)

def get_result_string(output):
    output = output.strip().split('\n')
    for line in output:
        if line.startswith("Dafny program verifier finished"):
            return line
    # expected="Dafny program verifier finished with 1 verified, 0 errors"
    # result_string = get_result_string(output)
    return None

def test_extract_errors_from_output():
    out = "Dafny program verifier finished with 4 verified, 0 errors"
    assert extract_errors_from_output(out)==0

def verify_dafny_file(file_path, compile=True):
    print("Should verify file:", file_path)
    dafny_file = file_path.split('/')[-1]
    output = config.DAFNY_OUT+dafny_file
    print("File name:", dafny_file)
    if compile:
        command = "{binary} '{path}' /out:{out} {target}".format(
            binary=config.DAFNY_BIN,
            path=file_path,
            out=output,
            target=config.DAFNY_TARGET
        )
    else:
        command = "{binary} verify '{path}'".format(
            binary=config.DAFNY_BIN,
            path=file_path,
        )

    print("Command:", command, flush=True)

    try:
        output = subprocess.check_output(['/usr/bin/bash','-c', command])
    except Exception as e:
        print("Caught exception")
        print("Error:",e,flush=True)
        return -1
    print("Dafny output:")
    # print(output,flush=True)
    # output = subprocess.run(['/usr/bin/bash','-c', command])
    output=output.decode('utf8')
    print("Output:", output, flush=True)
    expected="Dafny program verifier finished with 1 verified, 0 errors"
    result = output.strip().split('\n')[-1]
    result_string = get_result_string(output)
    print("Parsed result string:", result_string)
    nerrors = extract_errors_from_output(result_string)
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
# import re
# import sys
# from bandit.cli.main import main
@app.get("/bandit")
def run_bandit():
    print("Should run bandit", flush=True)
    python = '/usr/bin/python3'
    format = 'html'
    target = config.BANDIT_TARGET
    command = [python,'-m', 'bandit', '-r', target, '-f', format, '--exit-zero']
    print("Command:", command)

    try:
        print("Try to execute command",flush=True)
        output = subprocess.check_output(command)

        print("Bandit done")
        # print("Output:", output, flush=True)
        return HTMLResponse(content=output, status_code=200)
    except Exception as e:
        print("Error running bandit")
        print("Message:", str(e), flush=True)
        traceback.print_exc()
        return 500

@app.get("/cert")
def run_bandit():
    with open('/tmp/cert.pem') as f:
        cert = f.read()
    return cert

@app.get("/report")
def report():
    if not os.path.exists("/dev/attestation/report"):
        print("Cannot find `/dev/attestation/report`; are you running under SGX?")
        sys.exit(1)

    with open("/dev/attestation/my_target_info", "rb") as f:
        my_target_info = f.read()

    with open("/dev/attestation/target_info", "wb") as f:
        f.write(my_target_info)

    with open("/dev/attestation/user_report_data", "wb") as f:
        f.write(b'\0'*64)

    with open("/dev/attestation/report", "rb") as f:
        report = f.read()

    report_data = []
    report_data.append(f"Generated SGX report with size = {len(report)} and the following fields:")
    report_data.append(f"  ATTRIBUTES.FLAGS: {report[48:56].hex()}  [ Debug bit: {report[48] & 2 > 0} ]")
    report_data.append(f"  ATTRIBUTES.XFRM:  {report[56:64].hex()}")
    report_data.append(f"  MRENCLAVE:        {report[64:96].hex()}")
    report_data.append(f"  MRSIGNER:         {report[128:160].hex()}")
    report_data.append(f"  ISVPRODID:        {report[256:258].hex()}")
    report_data.append(f"  ISVSVN:           {report[258:260].hex()}")
    report_data.append(f"  REPORTDATA:       {report[320:352].hex()}")
    report_data.append(f"                    {report[352:384].hex()}")

    raw_data = []
    raw_data.append(f"Generated (RAW) SGX report with size = {len(report)} and the following fields:")
    raw_data.append(f"  ATTRIBUTES.FLAGS: {report[48:56]}  [ Debug bit: {report[48] & 2 > 0} ]")
    raw_data.append(f"  ATTRIBUTES.XFRM:  {report[56:64]}")
    raw_data.append(f"  MRENCLAVE:        {report[64:96]}")
    raw_data.append(f"  MRSIGNER:         {report[128:160]}")
    raw_data.append(f"  ISVPRODID:        {report[256:258]}")
    raw_data.append(f"  ISVSVN:           {report[258:260]}")
    raw_data.append(f"  REPORTDATA:       {report[320:352]}")
    raw_data.append(f"                    {report[352:384]}")

    str_report = "\n".join(report_data)
    print(str_report)
    print("\n".join(raw_data))
    return HTMLResponse(content=str_report.replace("\n", "<br>"), status_code=200)

if __name__=='__main__':
    print("Starting server...")
    # print(sys.path)
    # print("Config settings:")
    # print(config)
    # print(config.STAGING_DIR)
    # print(config.DAFNY_OUT)
    # print(config.DAFNY_BIN)
    # print(config.DAFNY_TARGET) 

    # print(res.text)
    # uvicorn.run("main:app", loop='asyncio', host='0.0.0.0', port=12341, reload=True)
    ENV = os.environ.get("ENV")

    # ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    # Use openssl to generate self signed cert:
    # openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
    if ENV=='local':
        cert_file = './local/ssl/cert.pem'
        key_file = './local/ssl/key.pem'
    else:
        cert_file='/tmp/cert.pem'
        key_file='/tmp/key.pem'
        # ssl_context.load_cert_chain('/tmp/cert.pem', keyfile='/tmp/key.pem')
    
    reload = True if ENV=='local' else False
    # reload = False
    print("Automatic reload is:", reload)

    uvicorn.run("main:app",
                loop='asyncio',
                host='0.0.0.0',
                port=12341,
                ssl_keyfile=key_file,
                ssl_certfile=cert_file,
                reload=reload
                )
