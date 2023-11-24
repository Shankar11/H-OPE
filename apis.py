import json
import http.client
import configparser
import similarcontext
from pandas import json_normalize
import os.path
import base64
from database import insertRecords,fetchRecords
from xrayclassifier import classifyxray, segmentxray
import requests

config = configparser.ConfigParser();
config.read("transaction.ini")
bearer_token = config['ACCESS']['bearer_token']
dev_url = config['ACCESS']['dev_url']
ot_url = config['ACCESS']['ot_url']
resource = config['ACCESS']['resource']

conn = http.client.HTTPSConnection(dev_url)

headersList = {
 "Accept": "*/*",
 "Authorization": "Bearer "+bearer_token,
 "Content-Type": "application/hal+json" 
}

def upload_file(file_content, content_type):
    print(content_type)
    payload = json.dumps({
    "data": file_content,
    "contentType": content_type,
    "offset": 0
    })

    conn.request("POST", resource+"/files/", payload, headersList)
    response = conn.getresponse()
    result = response.read()
    print(result)
    print(result.decode("utf-8"))
    jsnstr = json.loads(result.decode("utf-8"))
    parser = configparser.ConfigParser()
    parser.read('transaction.ini')
    parser.set('FILE_STORAGE', 'file_id',jsnstr['id'])
    with open('transaction.ini', 'w') as configfile:
        parser.write(configfile)
    return jsnstr['id']#,json_normalize(jsnstr)[['id','contentType','returnStatus.status','returnStatus.code']].to_json()

def download_file(file_id):
    payload = ""

    conn.request("GET", resource+"/files/"+file_id, payload, headersList)
    response = conn.getresponse()
    result = response.read()
    return result

def extract_file(file_id):
    
    conn = http.client.HTTPSConnection(dev_url)
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
					"value":"IE Invoice"
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

    conn.request("POST", resource+"/services/extractpage", payload, headersList)
    response = conn.getresponse()
    result = response.read()

    #print(result.decode("utf-8"))
    jsnstr = json.loads(result.decode("utf-8"))
    #due to the api not responding, we are retreiving it from a sample response file
    
    #with open('extract.json', 'r') as f:
    #    datajsn = json.load(f)
  
    #item = {}
    #ext_data=[]
    #jsonData=''
    #for i in range(len(datajsn['resultItems'][0]['values'][0]['value']['nodeList'])):
    #    item[datajsn['resultItems'][0]['values'][0]['value']['nodeList'][i]['name']] = datajsn['resultItems'][0]['values'][0]['value']['nodeList'][i]['data'][0]['value']
    #ext_data.append(item)

    #jsonData=json.dumps(ext_data)
    return jsnstr


def updateBearerToken(inp):
    parser = configparser.ConfigParser()
    parser.read('transaction.ini')
    parser.set('ACCESS', 'bearer_token',inp)
    with open('transaction.ini', 'w') as configfile:
        parser.write(configfile)
    return "success"

def get_apiresponse(msg):
    print('inside api resp ', msg.get("api_type") )
    if msg.get("api_type") == 'upload_file':
        upload_file(msg.get("file_content"), msg.get("content_type"))
        return fetchRecords()
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

def upload_files(filepath,filename):
    file_ext= os.path.splitext(filename)[1][1:]
    content_type="image/"+file_ext
    print('apis filepath ', filepath)
 
    with open(filepath, "rb") as imagefile:
        convert = base64.b64encode(imagefile.read())
    file_content = convert.decode('utf-8')
    return upload_file(file_content, content_type)

def classifyingxray(img_path):
    xlabel = classifyxray(img_path)
    xlabel = list(sorted(xlabel['preds'].items(), key=lambda x:x[1],reverse=True))[:4]
    return xlabel

def segmentingxray(img_path):
    return segmentxray(img_path)

def riskguard(file_path):
    headers = {
    "Authorization": "Bearer "+bearer_token, 
    }

    print(file_path)
    file_ext= os.path.splitext(file_path)[1][1:]
    files=[
  ('File',('sample patient.pdf',open(file_path,'rb'),'application/'+file_ext))
]
    response = requests.request("POST", "https://na-1-dev.api.opentext.com/mtm-riskguard/api/v1/process", headers=headers, data={}, files=files)
    #conn.request("POST", resource+"//mtm-riskguard/api/v1/process", {}, headersList ,files)
    #response = conn.getresponse()
    result = response.text
    print(result)
    return result