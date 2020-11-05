# !/usr/bin/python
# coding: utf-8
from app import app
from flask import render_template, request, redirect, url_for, abort, send_from_directory
from werkzeug.utils import secure_filename
import os
from app import RelationshipGrapher
from types import SimpleNamespace
import time

#app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 10 # 10 MB max file size
app.config['UPLOAD_EXTENSIONS'] = ['.xls', '.xlsx']
app.config['UPLOAD_PATH'] = 'uploads'
app.config['STATIC_PATH'] = 'static'
#print("Running in rgweb now")

@app.route('/')
def index():
   return render_template('index.html')
	
@app.route('/sampleFile.xlsx')
@app.route('/sampleFile')
def sample():
   return send_from_directory(app.config['STATIC_PATH'], "sample.xlsx")
	
@app.route('/', methods = ['POST'])
def upload_file():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            abort(400)
        fileTS = str(time.time())
        inputfileTS = fileTS + file_ext
        outputfileTS = fileTS +".png"
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], inputfileTS))
        #args = SimpleNamespace(**{'createcopy':False, 'excelfile' : os.path.join(app.config['UPLOAD_PATH'], inputfileTS), 'inputType':'excel', 'outputfile': os.path.join(app.config['UPLOAD_PATH'], outputfileTS), 'server':'http://www.plantuml.com/plantuml/img/', 'debug':False, 'LimitMaxLevel':0})
        args = SimpleNamespace(**{'createcopy':False, 'excelfile' : os.path.join(app.config['UPLOAD_PATH'], inputfileTS), 'inputType':'excel', 'outputfile': os.path.join(app.config['UPLOAD_PATH'], outputfileTS), 'server':'http://deiwapp1v.standardbank.co.za:5080/img/', 'debug':False, 'LimitMaxLevel':0})
        img = RelationshipGrapher.main(args)
    return send_from_directory("../"+app.config['UPLOAD_PATH'], outputfileTS)
    #return send_from_directory(os.path.join(app.config['UPLOAD_PATH'], outputfileTS))

#if __name__ == '__main__':
#    app.run(debug=True)
