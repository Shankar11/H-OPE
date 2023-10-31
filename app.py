from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from chatbot import get_response
from apis import get_apiresponse
import requests
import json
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
    
    # pulls information from the server
    if(request.method == 'GET'):
        
        # return index.html to the server
        return render_template("diagnosis.html")


    elif(request.method == 'POST'):
        
        api_type = request.form.get("api_type")
        if api_type == 'upload_file':
            tag = request.form.get("file_content")
            patterns = request.form.get("content_type")
        elif api_type == 'diagnosis_chat':
            tag = request.form.get("file_content")
        else:
            tag=''
            patterns=''

        resp = get_apiresponse(request.form)
        return render_template('apiresp.html', apidata=resp)

@app.route('/apiresp')
def apiresp():
    return render_template("apiresp.html")

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
    
    # pulls information from the server
    if(request.method == 'GET'):
        
        # return index.html to the server
        return render_template("repository.html")

    # sends the form data inputted by the user to the server 
    elif(request.method == 'POST'):
        
        # get user inputted values for zip code and country code
        api_type = request.form.get("api_type")
        if api_type == 'upload_file':
            tag = request.form.get("file_content")
            patterns = request.form.get("content_type")
        elif api_type == 'diagnosis_chat':
            tag = request.form.get("file_content")
        else:
            tag=''
            patterns=''

        resp = get_apiresponse(request.form)
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

if __name__ == "__main__":
    app.run(debug=True)

