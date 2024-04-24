

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
    output=output.decode('utf8')
    expected="Dafny program verifier finished with 1 verified, 0 errors"
    result = output.strip().split('\n')[0]
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

def verify_all():
    dafny_input_dir = '/data/tmp/'
    dafny_files=os.listdir(dafny_input_dir)
    print(dafny_files)
    for fname in dafny_files:
        path = dafny_input_dir+fname
        verify_dafny_file(path)
   
def rename_lib(src,dst):
    # mv does not seem to work
    # copy and remove instead
    # output = subprocess.check_output(['/usr/bin/bash','-c', 'mv '+ src + ' ' +dst])
    subprocess.check_output(['/usr/bin/bash','-c', 'cp -r '+ src + ' ' +dst])
    subprocess.check_output(['/usr/bin/bash','-c', 'rm -rf '+ src])
    print("Moved",src,'to',dst)

def run_abs():
    import sys
    from importlib.machinery import SourceFileLoader
    libpath = DAFNY_OUT+'Abs' + '-py'
    sys.path.append(libpath)
    foo = SourceFileLoader("abslib", libpath+"/module_.py").load_module()
    Abs = foo.default__.Abs
    res = Abs(-3)
    print("Result:", res)

def run_max():
    import sys
    from importlib.machinery import SourceFileLoader
    # sys.path.append('scripts/maxlib/')
    # sys.path.append('/data/lib/')
    # sys.path.append('/data/lib/maxlib/')
    libpath = DAFNY_OUT+'Max' + '-py'
    sys.path.append(libpath)
    foo = SourceFileLoader("maxlib", libpath+"/module_.py").load_module()
    Max = foo.default__.Max
    res = Max(3,5)
    print("Result:", res)

    return

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

def read_input():
    inputs = {}
    input_dir='/input/'
    input_files=os.listdir(input_dir)
    # print("Input files:", input_files)
    for fname in input_files:
        # print(fname)
        path=input_dir+fname
        with open(path, "r") as f:
            # print(f.read())
            inputs[fname]=f.read()
        print("-----")
    return inputs 

def create_dafny_files():
    inputs = read_input()
    print("Inputs:")
    for k,v in inputs.items():
        print(k,v)

    templates = read_templates()
    print("Templates:")
    for k,v in templates.items():
        print(k,v)

    for k in inputs:
        print("Input name:", k)
        template_name = replace_suffix(k, 'template')
        print("Template name:", template_name)
        if template_name in templates:
            print("Template found:")
            print(templates[template_name])
            dafny_file = merge(templates[template_name], inputs[k])
            # print("Mer")
            print("Merged:")
            print(dafny_file)
            dafny_file_name = replace_suffix(k,'dfy')
            print("File name:", dafny_file_name)
            path = '/data/tmp/'+dafny_file_name
            if not os.path.exists('/data/tmp/'):
                os.mkdir('/data/tmp/')
            with open(path,'w') as f:
                f.write(dafny_file)
                
        else:
            print("No corresponding template found")
        print("---")

def merge(template, body):
    print("Merge")
    print(template)
    print("with")
    print(body)
    print("----")
    return template+'\n{\n' + body + '\n}'

def replace_suffix(string, new_suffix):
    string = string.split('.')
    string[-1]=new_suffix
    return '.'.join(string)
    
if __name__=='__main__':
    print("Hello World!")
    # verify_max()
    # rename_lib('scripts/maxlib-py', 'scripts/maxlib')
    run_max()
    run_abs()
    # read_templates()
    # read_input()
    # create_dafny_files()
    # verify_all()
