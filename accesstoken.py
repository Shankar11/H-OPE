import http.client
import json
import pandas as pd
from configobj import ConfigObj
import configparser

conn = http.client.HTTPSConnection("na-1-dev.api.opentext.com")

headersList = {
 "Accept": "*/*",
 "Content-Type": "application/json" 
}

payload = json.dumps({
    "client_id": "1Jw2E3VTie13tC7vsg9yX81qIUxCeiVN",
    "client_secret": "oO4zZ0zE2at2cy9P",
    "grant_type": "password",
    "username": "sshankar11@gmail.com",
    "password": "Welcome@123"
})

conn.request("POST", "/tenants/539e378b-c644-4455-8be6-4c2018ebf9f4/oauth2/token", payload, headersList)
response = conn.getresponse()
result = response.read()
#print(result.decode("utf-8"))
resp_token = json.loads(result.decode("utf-8"))
print(resp_token['access_token'])


parser = configparser.ConfigParser()
parser.read('transaction.ini')
parser.set('ACCESS', 'bearer_token',resp_token['access_token'])
with open('transaction.ini', 'w') as configfile:
    parser.write(configfile)