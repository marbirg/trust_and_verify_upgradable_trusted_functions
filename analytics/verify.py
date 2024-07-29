
import sys
import os
import requests
import time
import json
import datetime

host='https://localhost:12341'

dafny_file_dir = './verified/'

def hello():
    url = host+'/verify'
    res = requests.post(url, json={'body':'my test data', 'name':'some name'}, verify=False)
    print(res.text)

def get_dafny_files():
    return os.listdir(dafny_file_dir)

def read_file_data(file_path):
    with open(file_path, 'r') as f:
        data = f.read()
    return data
    
def verify_dafny_code(name, body):
    url = host+'/verify'
    # print("Name:", name)
    # print("Body:")
    # print(body)
    data = {'name':name, 'body': body}
    start = time.time()
    res = requests.post(url, json=data, verify=False)
    elapsed = time.time()-start
    # print("Total elapsed time:", elapsed)

    # print(res.text)
    # print(res.json)
    res = json.loads(res.text)
    # print(res)
    result = {
        'errors': res['errors'],
        'verification_time':res['time'],
        'total_time': elapsed,
        'file':name
    }
    return result
    
def write_report_data(report_file_name, report_data):
    with open(report_file_name, 'w+') as f:
        f.write(json.dumps(report_data))

def read_json(fname:str):
    with open(fname,'r') as f:
        data = f.read()
    return json.loads(data) 

def create_empty_report(file_names):
    report_data = []
    for i in range(len(file_names)):
        name = file_names[i]
        result = {
            'errors': -2,
            'verification_time':-1,
            'total_time': -1,
            'file':name,
            'number':i+1
        }
        report_data.append(result)
    return report_data

if __name__=='__main__':
    if len(sys.argv)>1:
        print("Should re-verify",sys.argv[1])
        report_file_name = sys.argv[1]
        report_data = read_json(report_file_name)
    else:
        print("Should create new verification task")
        now = str(datetime.datetime.now()).replace(" ", '_') 
        report_file_name = 'verification.result-' + now + '.json'
        file_names = get_dafny_files()
        report_data = create_empty_report(file_names)

    # for d in report_data:
        # print(d)

    # paths = [dafny_file_dir + s for s in file_names]
    # data = read_file_data(paths[0])
    # for i in range(len(file_names)):
    # start = 750
    start = 0
    for i in range(start, len(report_data)):
        result = report_data[i]
        if result['errors']==0:
            continue

        print(result)
        # name = file_names[i]
        name = result['file']
        # if not name.find(" ")>=0:
            # continue
        # print(name)
        body = read_file_data(dafny_file_dir+name)
        # print(body)

        print(i+1,"/",len(report_data), 'Verify:', name)
        # exit()
        result = verify_dafny_code(name, body)
        result['number']=i+1
        print(result)
        # report_data.append(result)
        report_data[i] = result
        # break
        print("report_file_name:", report_file_name)
        write_report_data(report_file_name, report_data)
