import os
import sys
import logging
import time
import requests
from typing import Optional, Dict, Any, Tuple
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# API Keys
API_KEYS = {}

# Load environment variables
load_dotenv()

# Set API keys from environment or use defaults
API_KEYS['OPEN_WEATHER_API_KEY'] = os.getenv('OPEN_WEATHER_API_KEY', 'cc0a492f65628c8da903b9c7190242aa')

class WeatherService:
    def __init__(self):
        # Initialize API keys
        self.weather_api_key = API_KEYS['OPEN_WEATHER_API_KEY']
        self._setup_health_check()
        logger.info('WeatherService initialized successfully')
    
    def _setup_health_check(self):
        # Setup health check for API services
        self.last_health_check = time.time()
        self.health_check_interval = 300  # 5 minutes
    
    def get_user_input(self) -> Tuple[str, str]:
        """Get city and country input from user.
        
        Returns:
            Tuple[str, str]: City and country entered by user
        """
        while True:
            try:
                print('
Enter location details:')
                city = input('City: ').strip()
                country = input('Country: ').strip()
                
                if not city or not country:
                    print('Error: City and country cannot be empty. Please try again.')
                    continue
                
                return city, country
            except Exception as e:
                logger.error(f'Error getting user input: {e}')
                print('Error: Invalid input. Please try again.')
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_location(self, city: str, country: str) -> Dict[str, Any]:
        """Get location coordinates for the given city and country.
        
        Args:
            city (str): City name
            country (str): Country name
        
        Returns:
            Dict[str, Any]: Location data including coordinates
        """
        try:
            logger.info(f'Fetching location info for {city}, {country}...')
            # Get location from OpenWeatherMap
            response = requests.get(
                f'http://api.openweathermap.org/geo/1.0/direct?q={city},{country}&limit=1&appid={self.weather_api_key}'
            )
            response.raise_for_status()
            locations = response.json()
            
            if not locations:
                logger.error(f'No location data found for {city}, {country}')
                raise ValueError(f'No location data found for {city}, {country}')
            
            location = locations[0]
            city = location.get('name', city)
            country = location.get('country', country)
            lat = location.get('lat', 0.0)
            lon = location.get('lon', 0.0)
            
            logger.info(f'Location: {city}, {country} ({lat},{lon})')
            return {'city': city, 'country': country, 'latitude': lat, 'longitude': lon}
        except Exception as e:
            logger.error(f'Error getting location: {e}')
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        try:
            logger.info('Fetching weather data...')
            response = requests.get(
                f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.weather_api_key}&units=metric'
            )
            response.raise_for_status()
            weather = response.json()
            logger.info('Weather data retrieved successfully')
            return weather
        except Exception as e:
            logger.error(f'Error getting weather: {e}')
            raise
    
    def format_weather_output(self, location: Dict[str, Any], weather: Dict[str, Any]) -> str:
        try:
            city = location['city']
            country = location['country']
            temp = weather['main']['temp']
            feels_like = weather['main']['feels_like']
            condition = weather['weather'][0]['description']
            humidity = weather['main']['humidity']
            wind_speed = weather['wind']['speed']
            
            output = f'''
Current weather for {city}, {country}
Temperature: {temp}°C (feels like {feels_like}°C)
Condition: {condition.title()}
Humidity: {humidity}%
Wind Speed: {wind_speed} m/s
'''
            return output
        except Exception as e:
            logger.error(f'Error formatting weather output: {e}')
            raise

def main() -> None:
    try:
        logger.info('Starting weather application...')
        service = WeatherService()
        
        while True:
            try:
                # Get user input
                city, country = service.get_user_input()
                
                # Get location
                location = service.get_location(city, country)
                
                # Get weather
                weather = service.get_weather(location['latitude'], location['longitude'])
                
                # Format and display output
                output = service.format_weather_output(location, weather)
                print(output)
                
                # Ask if user wants to check another location
                if input('
Check weather for another location? (y/n): ').lower() != 'y':
                    break
                
            except ValueError as e:
                print(f'
Error: {e}')
                if input('Try again? (y/n): ').lower() != 'y':
                    break
            except Exception as e:
                logger.error(f'Application failed: {e}')
                print(f'
Error: {e}')
                if input('Try again? (y/n): ').lower() != 'y':
                    break
        
        logger.info('Application completed successfully')
    except Exception as e:
        logger.error(f'Application failed: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()