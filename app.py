from flask import Flask,request, url_for, redirect, render_template, jsonify
from pycaret.classification import *
import pandas as pd
import pickle
import numpy as np

app = Flask(__name__)

class_obt={0:'This patient not have heart disease',1:'This patient have heart disease'}

model = load_model('heartdiseae1235')


cols = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak','slope', 'ca', 'thal']

@app.route('/')
def home():
    return render_template("prediction.html")

@app.route('/predict',methods=['POST'])
def predict():
    int_features = [x for x in request.form.values()]
    final = np.array(int_features)
    data_unseen = pd.DataFrame([final], columns = cols)
    prediction = predict_model(model, data=data_unseen)
    
    prediction = int(prediction.Label[0])
  
    result = class_obt.get(prediction)
    return render_template('predictresult.html',result=result)

@app.route('/predict_api',methods=['POST'])
def predict_api():
    data = request.get_json(force=True)
    data_unseen = pd.DataFrame([data])
    prediction = predict_model(model, data=data_unseen)
    output = prediction.Label[0]
    return jsonify(output)

if __name__ == '__main__':
    app.run("0.0.0.0")
