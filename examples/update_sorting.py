
import requests

HOST='https://localhost:12341'

def deploy_sort():
    body_path='./dafny.examples/bubble_sort.body'
    # body_path='./dafny.examples/merge.sort.body'
    url = HOST+'/deploy'
    name = 'Sort'
    with open(body_path,'r') as f:
        body = f.read()
    print(body)
    data = {'name': name, 'body': body}
    res = requests.post(url, json=data, verify=False)
    print(res)
    print(res.text)

if __name__=='__main__':
    deploy_sort()
