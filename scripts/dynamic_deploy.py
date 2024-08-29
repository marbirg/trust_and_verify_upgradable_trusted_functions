import os
import sys

import traceback
import importlib
import subprocess
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse

from importlib.machinery import SourceFileLoader

from fastapi import APIRouter

from pydantic import BaseModel
import base64

from lib.crypto import decrypt_aes

from models import CodeItem, RunSpec

from conf_lib import get_config
config = get_config()

router = APIRouter()

_KEYS = {}
_DATA = {}

@router.post("/deploy")
async def deploy(codeObj:CodeItem):
    print(codeObj)
    path = config.DYNAMIC_CODE + codeObj.name
    print(path)
    if not os.path.exists(config.DYNAMIC_CODE):
        os.mkdir(config.DYNAMIC_CODE)
    with open(path,'w') as f:
        f.write(codeObj.body)
        print("Written file",path )

    
@router.post("/run")
async def deploy(runSpec:RunSpec):
    sys.path.append(config.DYNAMIC_CODE)
    module = importlib.import_module(runSpec.name)
    module.main(*runSpec.argv, **runSpec.argd)
    # module.main()
    # hello.main()
    # return SourceFileLoader(libname, module_path).load_module()

    # print("Hello world")
    # print(runSpec)

@router.post("/verify")
async def verify(name:str, baseline:str=None):
    # print("Verify code:")
    # print("Name:", name)
    # print('Baseline:',baseline)
    print("Should run bandit", flush=True)

    python = '/usr/bin/python3'
    format = 'html'
    format = 'json'
    target = config.DYNAMIC_CODE+name

    command = [python,'-m', 'bandit', '-r', target, '-f', format, '--exit-zero']
    if baseline:
        baseline_path = config.STAGING_DIR+'baseline.json'
        with open(baseline_path, 'w') as f:
           f.write(baseline) 
           command = [python,'-m', 'bandit', '-r', target, '-f', format, '--exit-zero','-b',baseline_path]
    try:
        print("Try to execute command",flush=True)
        print("Command:", command)
        output = subprocess.check_output(command)

        print("Bandit done")
        # print("Output:", output, flush=True)
        return HTMLResponse(content=output, status_code=200)
    except Exception as e:
        print("Error running bandit")
        print("Message:", str(e), flush=True)
        traceback.print_exc()
        return 500

