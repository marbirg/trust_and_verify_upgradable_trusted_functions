
import os
import subprocess
import config
import time
import csv
import datetime
data_dir = "./DafnyBench/DafnyBench/dataset/ground_truth"
def extract_errors_from_output(output):
    errors = output.split(',')[-1].strip()
    nerrors = errors.split(" ")[0]
    return int(nerrors)

def verify_dafny_file(file_path):
    # print("Should verify file:", file_path)
    # dafny_file = file_path.split('/')[-1]
    # output = config.DAFNY_OUT+dafny_file
    # print("File name:", dafny_file)
    command = "{binary} verify '{path}'".format(
        binary=config.DAFNY_BIN,
        path=file_path,
    )
    # print("Command:", command)

    try:
        output = subprocess.check_output(['/usr/bin/bash','-c', command], timeout=600)
    except Exception as e:
        print("Caught exception")
        print("Command:", command)
        print("Error:",e,flush=True)
        return -1, e
    # print("Dafny output:")
    # print(output,flush=True)
    # output = subprocess.run(['/usr/bin/bash','-c', command])
    output=output.decode('utf8')
    # print("Output:", output, flush=True)
    expected="Dafny program verifier finished with 1 verified, 0 errors"
    result = output.strip().split('\n')[-1]
    nerrors = extract_errors_from_output(result)
    return nerrors, output
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
   


if __name__=='__main__':
    files = os.listdir(data_dir)
    # print(files)
    print("Number of files:", len(files))
    result = []
    errors = []
    skipped = []
    skip_index=[172, 229]
    for i in range(len(files)):
        f = files[i]
        file_name = f.split('/')[-1]
        if i in skip_index:
            skipped.append([file_name])
            print("Skipping", file_name)
            with open('skipped.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(skipped)
            continue
        # index = file_name.find(" ")
        # if index<0:
        #     continue
        print(datetime.datetime.now())
        print(i,"/",len(files),"Try to verify", file_name)
        start = time.time()
        nerrors, output = verify_dafny_file(data_dir+'/'+f)
        stop = time.time()
        if nerrors!=0:
            print("Error verifying", file_name)
            print(output)
            errors.append([file_name])
            with open('errors.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(errors)
            continue
        else:
            print(file_name, 'verified in', stop-start, 's')
            result.append([file_name, stop-start])

        print()
        with open('result.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(result)
