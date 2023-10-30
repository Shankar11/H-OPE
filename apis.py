import json
import http.client
import configparser
import similarcontext
from pandas import json_normalize

config = configparser.ConfigParser();
config.read("transaction.ini")
bearer_token = config['ACCESS']['bearer_token']
dev_url = config['ACCESS']['dev_url']
ot_url = config['ACCESS']['ot_url']

conn = http.client.HTTPSConnection(dev_url)

headersList = {
 "Accept": "*/*",
 "Authorization": "Bearer "+bearer_token,
 "Content-Type": "application/hal+json" 
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
    return json_normalize(jsnstr)[['id','contentType','returnStatus.status','returnStatus.code']].to_json()

def download_file(file_id):
    payload = ""

    conn.request("GET", "/capture/cp-rest/v2/session/files/"+file_id, payload, headersList)
    response = conn.getresponse()
    result = response.read()
    return result

def extract_file(file_id):
    conn = http.client.HTTPSConnection(ot_url)
    payload = json.dumps({
    "serviceProps":
    [
        {
            "name":"Env",
            "value":"D"
        },
        {
            "name":"IncludeOcrData",
            "value":"True"
        },
        {
            "name":"Project",
            "value":"InformationExtraction"
        }
    ],
    "requestItems":
    [
        {
            "nodeId":1,
            "values": 
            [
            	{
					"name":"DocumentTypeName",
					"value":"IE Blood Test Report"
				},
				{
					"name":"TemplateId",
					"value":""
				},
				{
					"name":"PageIndex",
					"value":"0"
				}
            ],
            "files":
            [
                {
                    "name":"blood-report",
                    "value": file_id,
                    "contentType":"image/tiff",
                    "fileType":"tiff"
                }
            ]
        }
    ]
})

    conn.request("POST", "/capture/cp-rest/v2/session/services/extractpage", payload, headersList)
    response = conn.getresponse()
    result = response.read()

    print(result.decode("utf-8"))
    jsnstr = json.loads(result.decode("utf-8"))
    return json_normalize(jsnstr)


def updateBearerToken(inp):
    parser = configparser.ConfigParser()
    parser.read('transaction.ini')
    parser.set('ACCESS', 'bearer_token',inp)
    with open('transaction.ini', 'w') as configfile:
        parser.write(configfile)
    return "success"

def get_apiresponse(msg):
    if msg.get("api_type") == 'upload_file':
        return upload_file(msg.get("file_content"), msg.get("content_type"))
    elif msg.get("api_type") == 'diagnosis_chat':
        return   similarcontext.similarity_finder(msg.get("file_content"))
    elif msg.get("api_type") == 'save_bearer_token':
        return   updateBearerToken(msg.get("file_content"))
    elif msg.get("api_type") == 'download_file':
        return   download_file(msg.get("file_content"))
    elif msg.get("api_type") == 'extract_file':
        return   extract_file(msg.get("file_content"))
    else:
        print('NA')
