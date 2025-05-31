import unittest
from unittest.mock import patch, MagicMock
from src.main import WeatherService, main

class TestWeatherService(unittest.TestCase):
    def setUp(self):
        self.service = WeatherService()
    
    @patch('builtins.input')
    def test_get_user_input(self, mock_input):
        mock_input.side_effect = ['London', 'UK']
        city, country = self.service.get_user_input()
        self.assertEqual(city, 'London')
        self.assertEqual(country, 'UK')
    
    @patch('src.utils.helpers.make_api_request')
    def test_api_request_retry(self, mock_request):
        mock_request.side_effect = [Exception(), Exception(), {'status': 'success'}]
        result = self.service.get_weather(0, 0)
        self.assertEqual(result['status'], 'success')
    
    def test_format_weather_output(self):
        location = {'city': 'Test City', 'country': 'Test Country'}
        weather = {'main': {'temp': 20, 'feels_like': 22, 'humidity': 65}, 'weather': [{'description': 'clear sky'}], 'wind': {'speed': 5.0}}
        output = self.service.format_weather_output(location, weather)
        self.assertIn('Test City', output)
        self.assertIn('20°C', output)
        self.assertIn('Clear Sky', output)
        self.assertIn('65%', output)
        self.assertIn('5.0 m/s', output)