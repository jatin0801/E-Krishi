from flask import Flask, render_template, request, Markup, redirect
import numpy as np
import pandas as pd
import pickle
import requests
from utils.disease import disease_dic
import pickle
import io
import torch
from torchvision import transforms
from PIL import Image
from utils.model import ResNet9

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


def weather_fetch(city_name):
    api_key = "6ee1dc7bb1bc5a8a16ba813050149c05"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()

    if x["cod"] != "404":
        y = x["main"]

        temperature = round((y["temp"] - 273.15), 2)
        humidity = y["humidity"]
        return temperature, humidity
    else:
        return None


crop_recommendation_model = pickle.load(
    open('Models/model.pkl', 'rb'))


@app.route('/crop-planning/')
def crop_planning():
    return render_template("crop.html")


@ app.route('/crop-predict/', methods=['POST'])
def crop_prediction():
    title = 'e-Krishi: A one stop portal'

    if request.method == 'POST':
        N = int(request.form['nitrogen'])
        P = int(request.form['phosphorous'])
        K = int(request.form['potassium'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])
        city = request.form.get("city")

        if weather_fetch(city) != None:
            temperature, humidity = weather_fetch(city)
            data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
            my_prediction = crop_recommendation_model.predict(data)
            final_prediction = my_prediction[0]
            print()
            print("Final Prediction", final_prediction)
            return render_template('crop-result.html', prediction=final_prediction.capitalize(), title=title)
        else:
            return render_template('try_again.html', title=title)


@app.route('/sell/')
def sell():
    return render_template("sell.html")

@app.route('/buy/')
def buy():
    return render_template("buy.html")

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")


if __name__ == "__main__":
    app.run()
