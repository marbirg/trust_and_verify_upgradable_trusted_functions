

import os
import subprocess

# print("Hello world from python")
DAFNY_BIN = "/usr/lib/dafny/dafny"
DAFNY_OUT = "/data/verified/"

DAFNY_IN = "scripts"
DAFNY_TARGET = '/compileTarget:py'
LIB = '/data/lib/'

def verify_max():
    libname='maxlib'

    command = "/usr/lib/dafny/dafny scripts/Max.dfy /out:/scripts/maxlib /compileTarget:py"
    command = "{binary} {base}/{script} /out:{out} {target}".format(
        binary=DAFNY_BIN,
        base=DAFNY_IN,
        script='Max.dfy',
        out=DAFNY_OUT+libname,
        target=DAFNY_TARGET
    )
    print("Command:", command)
    # return
    # command = "/usr/lib/dafny/dafny verify scripts/Abs.dfy"

    output = subprocess.check_output(['/usr/bin/bash','-c', command])
    output=output.decode('utf8')
    expected="Dafny program verifier finished with 1 verified, 0 errors"
    result = output.strip().split('\n')[0]
    if result==expected:
        print("Verification successfull")
        print("Move and rename module")
        src=DAFNY_OUT+libname+'-py'
        dst=LIB+libname
        # rename_lib(src,dst)
    else:
        print("Verification not successfull")
        print(result)
        print(expected)
        print("---")


    # Print the output
    # print("Command:", command)
    print("Result:",output)
    
def rename_lib(src,dst):
    # mv does not seem to work
    # copy and remove instead
    # output = subprocess.check_output(['/usr/bin/bash','-c', 'mv '+ src + ' ' +dst])
    subprocess.check_output(['/usr/bin/bash','-c', 'cp -r '+ src + ' ' +dst])
    subprocess.check_output(['/usr/bin/bash','-c', 'rm -rf '+ src])
    print("Moved",src,'to',dst)

def run_max():
    import sys
    from importlib.machinery import SourceFileLoader
    # sys.path.append('scripts/maxlib/')
    # sys.path.append('/data/lib/')
    # sys.path.append('/data/lib/maxlib/')
    sys.path.append('/data/verified/maxlib-py/')
    res = None
    # foo = SourceFileLoader("maxlib", "/data/lib/maxlib/module_.py").load_module()
    foo = SourceFileLoader("maxlib", "/data/verified/maxlib-py/module_.py").load_module()
    print(dir(foo))
    Max = foo.default__.Max
    res = Max(3,5)
    # print(foo.path)
    # foo.module__
    # import maxlib.module_ as m
    # from maxlib.module_ import default__ as ml
    # res = m.default__.Max(3,2)
    # res = ml.Max(5,8)
    print("Result:", res)

if __name__=='__main__':
    print("Hello World!")
    # verify_max()
    # rename_lib('scripts/maxlib-py', 'scripts/maxlib')
    run_max()
