import requests

# from pydantic import validate_call
# import json

# import config
# from common import create_and_store_users, load_users, Base64Encoder
# from common import encrypt_data

import urllib3  
# Suppress only the single warning from urllib3.
urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

HOST='https://localhost:12341'
success_response = "\"Voting verified with 0 errors\""
error_response = "\"Verification did not succeed\""

def deploy_voting(body_path):
    url = HOST+'/deploy'
    name = 'Voting'
    with open(body_path,'r') as f:
        body = f.read()
    data = {'name': name, 'body': body}
    res = requests.post(url, json=data, verify=False)
    return res.text


if __name__=='__main__':
    correct_voting = './dafny.examples/Voting.body'
    faulty_voting = './dafny.examples/faulty.Voting.body'

    response = deploy_voting(correct_voting)
    assert response == success_response

    response = deploy_voting(faulty_voting)
    assert response == error_response 
    print("Succes")
