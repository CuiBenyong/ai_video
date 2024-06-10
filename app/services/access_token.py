
import requests
import json
import os
import time

baidu_llm_access_token = ""
token_expired_time = 0
 
def save_access_token(access_token, expires_in):
    os.environ['ACCESS_TOKEN'] = access_token
    os.environ['TOKEN_EXPIRED_TIME'] = str(time.time() + expires_in)
 
def load_access_token():
    return os.environ.get('ACCESS_TOKEN')

def is_token_expired():
    expired_time = os.environ.get('TOKEN_EXPIRED_TIME') or '0'
    now = time.time()
    return now > (float(expired_time) - 1200)

def getAccessToken():
    
    baidu_llm_access_token = load_access_token()
    if(not is_token_expired()):
        print("access token>", baidu_llm_access_token)
        return baidu_llm_access_token
    
    url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=2aPfmurQ6X8ofvCDzXz0Nxjc&client_secret=B7QuSqv0CnQ8pELvYmwRcI75YyowJTVZ"
    
    payload = ""
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    res = json.loads(response.text)
    
    baidu_llm_access_token = res["access_token"]
    expires_in = res["expires_in"]
    save_access_token(baidu_llm_access_token, expires_in)
    return baidu_llm_access_token