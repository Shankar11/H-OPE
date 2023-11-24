import json
import requests

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from chatbot import get_response
from apis import get_apiresponse,upload_files,download_file,classifyingxray,segmentingxray,riskguard,extract_file
import database
from werkzeug.utils import secure_filename
import os
from database import insertRecords,fetchRecords
import time
import similarcontext

app = Flask(__name__)
CORS(app)

@app.get("/")

def index_get():
    return render_template("landing.html")

@app.route('/login')
def login():
    return render_template("login.html")

#@app.route('/diagnosis')
#def diagnosis():
    #return render_template("diagnosis.html")

@app.route('/diagnosis', methods = ["GET", "POST"])
def diagnosis():
    
    print("file_content  diagnosis")
    # pulls information from the server
    if(request.method == 'GET'):
        
        # return index.html to the server
        return render_template("diagnosis.html")


    elif(request.method == 'POST'):
        print("file_content POST")
        api_type = request.form.get("api_type")
        resp = get_apiresponse(request.form)
        if api_type == 'upload_file':
            tag = request.form.get("file_content")
            patterns = request.form.get("content_type")
            resp = fetchRecords()
            print("file_content")
            print(resp)
        elif api_type == 'diagnosis_chat':
            tag = request.form.get("file_content")
        elif api_type == 'extract_file':
            return render_template('resp.html', apidata=resp)   
        else:
            tag=''
            patterns=''

        
        return render_template('apiresp.html', apidata=resp)

@app.route('/apiresp')
def apiresp():
    return render_template("apiresp.html")

@app.route('/response')
def response():
    return render_template("response.html")

@app.route('/analysis')
def analysis():
    return render_template("analysis.html")

@app.route('/btnClick', methods = ["GET", "POST"])
def btnClick():
    resp1=''
    print('btnClick')
    print(request.form.get("fid"))
    print(request.form.get("fpath"))
    print(request.form.get("fname"))
    print(request.form.get("btnaction"))
    if(request.method == 'GET'):
        sqlresp = fetchRecords()
        return render_template("apiresp.html",apidata=sqlresp)
    else:
        if(request.form.get("btnaction")=='extract'):
            resp1 = extract_file(request.form.get("fid"))
        elif(request.form.get("btnaction")=='download'):
            resp1 = download_file(request.form.get("fid"))
        elif(request.form.get("btnaction")=='analyse'):
            if(request.form.get("fname").__contains__('xray')):               
                clx = classifyingxray('./static/uploads/'+request.form.get("fname"))
                sgx = segmentingxray('./static/uploads/'+request.form.get("fname"))
                resp1 = clx,sgx
                return render_template("analysis.html",apidata=resp1)
            print(request.form.get("fname") ,'   ' ,request.form.get("fname").__contains__('xray'))
            return render_template("response.html",genericdata="Not a valid xray file")
        elif(request.form.get("btnaction")=='compliance'):
            resp1 = riskguard(fullpath+request.form.get("fname"))
            return render_template("response.html",genericdata=resp1)    
        else:
            print('btn click else')            
        
        return render_template("response.html",genericdata=resp1)

@app.route('/faq')
def faq():
    return render_template("faq.html")

# @app.route('/repository')
# def repository():
#     return render_template("repository.html")

@app.post("/predict")
def predict():
    text = request.get_json().get("message")
    #TODO : check if text is valid
    response = get_response(text)
    message = {"answer" : response}
    print(text)
    return jsonify(message)

@app.post("/answer")
def answer():
    text = request.get_json().get("message")
    message = similarcontext.similarity_finder(text)
    #TODO : check if text is valid
    #response = get_response(text)
    #message = {"answer" : response}
    print(message)
    return message.to_json()


@app.route('/repository', methods = ["GET", "POST"])
def index():
    print("file_content  repository")
    # pulls information from the server
    if(request.method == 'GET'):
        
        # return index.html to the server
        return render_template("repository.html")

    # sends the form data inputted by the user to the server 
    elif(request.method == 'POST'):
        resp = get_apiresponse(request.form)
        # get user inputted values for zip code and country code
        api_type = request.form.get("api_type")
        if api_type == 'upload_file':
            tag = request.form.get("file_content")
            patterns = request.form.get("content_type")
            resp = fetchRecords()
        elif api_type == 'diagnosis_chat':
            tag = request.form.get("file_content")
        else:
            tag=''
            patterns=''

        
        print(request.form)
        # send request to openweathermap API
       # openweather = requests.get("https://api.openweathermap.org/data/2.5/weather?zip={},{}&appid={}&units=imperial".format(tag, patterns, ("API_KEY")))
        
        # return weather.html to the server
        #dataj = '{"name":"John", "age":30, "car":null}'
        return render_template('apiresp.html', apidata=resp)

# pass the zipcode and country code as keyword arguments

# @app.route('/<tag>/<patterns>', methods = ["GET", "POST"])
# def updateDisease1():

  #   tag = request.form.get("tag")
  #   patterns = request.form.get("patterns")
    # send request to openweathermap API
  #   openweather = requests.get("https://api.openweathermap.org/data/2.5/weather?zip={},{}&appid={}".format(tag, patterns, ("API_KEY")))
    
    # test openweather API
  #   print(openweather.json())
@app.route('/upload', methods = ['GET', 'POST'])
def uploadfile():
   if request.method == 'POST': # check if the method is post
      files = request.files.getlist('files')
      for f in files:
          f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
          time_to_wait = 10
          time_counter = 0
          while not os.path.isfile(os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))):
              time.sleep(1)
              time_counter += 1
              if time_counter > time_to_wait:break
          
          print(os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))) # this will secure the file
          fileid= upload_files(os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename))),f.filename)
          
          insertRecords(f.filename,fileid,os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename))))
          resp = fetchRecords()
          
      return render_template('apiresp.html', apidata=resp)# fileid"File uploaded successfully"
   if(request.method == 'GET'):
        # return index.html to the server
        return render_template("diagnosis.html")

@app.route('/viewdocs', methods = ["GET", "POST"])
def viewdocs():

    if(request.method == 'POST'):
        resp = fetchRecords()
        return render_template('apiresp.html', apidata=resp)
    else:
        return render_template("diagnosis.html") 
   
# Creating the upload folder
fullpath = 'C:/ShS/Python/WS/HOPE/H-OPE-main/static/uploads/'
upload_folder = "static/uploads/"
if not os.path.exists(upload_folder):
   os.mkdir(upload_folder)

app.config['UPLOAD_FOLDER'] = upload_folder

if __name__ == "__main__":
    app.run(debug=True)

