from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

OPEN_WEATHER_API_KEY = os.getenv('OPEN_WEATHER_API_KEY')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        lat = request.form['lat']
        lon = request.form['lon']
        url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPEN_WEATHER_API_KEY}&units=metric'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return render_template('index.html', data=data)
        else:
            return render_template('index.html', error='Failed to fetch weather data')
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)