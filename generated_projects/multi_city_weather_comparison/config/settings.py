import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Application settings
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# API settings
API_SETTINGS = {}
API_SETTINGS['WEATHER_API_URL'] = 'https://api.openweathermap.org/data/2.5/weather'
API_SETTINGS['GEO_API_URL'] = 'http://api.openweathermap.org/geo/1.0/direct'
API_SETTINGS['WEATHER_API_RATE_LIMIT'] = 1000  # requests per day

# Retry settings
RETRY_SETTINGS = {}
RETRY_SETTINGS['MAX_ATTEMPTS'] = 3
RETRY_SETTINGS['MIN_WAIT'] = 4  # seconds
RETRY_SETTINGS['MAX_WAIT'] = 10  # seconds

# Logging settings
LOG_SETTINGS = {}
LOG_SETTINGS['FORMAT'] = '%(asctime)s - %(levelname)s - %(message)s'
LOG_SETTINGS['FILE'] = 'app.log'
LOG_SETTINGS['LEVEL'] = 'INFO'