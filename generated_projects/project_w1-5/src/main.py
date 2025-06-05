from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

OPEN_WEATHER_API_KEY = os.getenv('OPEN_WEATHER_API_KEY')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        city = request.form.get('city')
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPEN_WEATHER_API_KEY}&units=metric'
        response = requests.get(url)
        data = response.json()
        return render_template('index.html', data=data)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)