import json
import http.client
import configparser


config = configparser.ConfigParser();
config.read("transaction.ini")
bearer_token = config['ACCESS']['bearer_token']

conn = http.client.HTTPSConnection("na-1-dev.api.opentext.com")

headersList = {
 "Accept": "*/*",
 "Authorization": "Bearer "+bearer_token,
 "Content-Type": "application/json" 
}

def upload_file(file_content, content_type):
    payload = json.dumps({
    "data": file_content,
    "contentType": content_type,
    "offset": 0
    })

    conn.request("POST", "/capture/cp-rest/v2/session/files/", payload, headersList)
    response = conn.getresponse()
    result = response.read()

    print(result.decode("utf-8"))
    jsnstr = json.loads(result.decode("utf-8"))
    parser = configparser.ConfigParser()
    parser.read('transaction.ini')
    parser.set('FILE_STORAGE', 'file_id',jsnstr['id'])
    with open('transaction.ini', 'w') as configfile:
        parser.write(configfile)
    return jsnstr

def get_apiresponse(msg):
    if msg.get("api_type") == 'upload_file':
        return upload_file(msg.get("file_content"), msg.get("content_type"))
    else:
        print('NA')
