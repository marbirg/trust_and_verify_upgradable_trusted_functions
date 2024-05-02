
import sys
from fastapi import FastAPI
import uvicorn
import os
import subprocess
import time
from threading import Thread
# from multiprocessing import Process

STAGING_DIR = '/data/tmp/'
DAFNY_OUT = "/data/verified/"
DAFNY_BIN = "/usr/lib/dafny/dafny"
DAFNY_TARGET = '/compileTarget:py'

app=FastAPI()
@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/inputs")
async def get_inputs():
    inputs = read_input()
    create_dafny_files(inputs)

    path_list = []
    for fname in inputs:
        fname = replace_suffix(fname,'dfy')
        path_list.append(STAGING_DIR + fname)
    # return path_list
    res = verify_all(path_list)
    print("Result:", res)

    return {"status":200}
    return res
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
    output = DAFNY_OUT+dafny_file
    print("File name:", dafny_file)
    command = "{binary} {path} /out:{out} {target}".format(
        binary=DAFNY_BIN,
        path=file_path,
        out=output,
        target=DAFNY_TARGET
    )
    print("Command:", command)

    output = subprocess.check_output(['/usr/bin/bash','-c', command])
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
    input_dir='/input/'
    input_files=os.listdir(input_dir)
    for fname in input_files:
        path=input_dir+fname
        with open(path, "r") as f:
            inputs[fname]=f.read()
        print("-----")
    return inputs 

def read_templates():
    templates = {}
    template_dir='/templates/'
    template_files=os.listdir(template_dir)
    for fname in template_files:
        path=template_dir+fname
        with open(path, "r") as f:
            # print(f.read())
            templates[fname]=f.read()
    return templates

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
            path = STAGING_DIR+dafny_file_name
            if not os.path.exists(STAGING_DIR):
                os.mkdir(STAGING_DIR)
            with open(path,'w') as f:
                f.write(dafny_file)
        else:
            print("No corresponding template found")
        print("---")

if __name__=='__main__':
    print("Hello world!")
    print(sys.path)
    uvicorn.run("main:app", loop='asyncio', host='0.0.0.0', port=12341)
