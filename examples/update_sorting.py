
import requests
import urllib3  
# Suppress only the single warning from urllib3.
urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

HOST='https://localhost:12341'
success_response = "\"Sort verified with 0 errors\""

def deploy_sort(body_path):
    url = HOST+'/deploy'
    name = 'Sort'
    with open(body_path,'r') as f:
        body = f.read()
    data = {'name': name, 'body': body}
    res = requests.post(url, json=data, verify=False)
    return res.text

if __name__=='__main__':
    bubble_sort_body_path='./dafny.examples/bubble_sort.body'
    merge_sort_body_path='./dafny.examples/merge.sort.body'
    bubble_response = deploy_sort(bubble_sort_body_path)
    assert bubble_response == success_response
    merge_response = deploy_sort(merge_sort_body_path)
    assert merge_response == success_response
    print("Success")
