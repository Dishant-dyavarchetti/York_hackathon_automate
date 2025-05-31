# auto_location_weather_widget

# Setup Instructions

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python src/main.py
   ```

## Development

- Format code: `black .`
- Lint code: `flake8`
- Type checking: `mypy .`

## Monitoring

- Check application logs in `app.log`
- Monitor API rate limits and health status
- Use Prometheus metrics for monitoring

## Usage

1. Run the application
2. Enter the city name when prompted
3. Enter the country name when prompted
4. View the weather information
5. Choose to check weather for another location or exit

## Output Format

The application will display weather information in the following format:

```
Current weather for [City], [Country]
Temperature: [Temp]°C (feels like [Feels Like]°C)
Condition: [Weather Condition]
Humidity: [Humidity]%
Wind Speed: [Wind Speed] m/s
```

## Python Code Style

This project follows strict Python code style guidelines:

1. Use 4 spaces for indentation (NO tabs)
2. Maximum line length of 88 characters (Black formatter standard)
3. Follow PEP 8 style guide
4. Use proper indentation for all code blocks
5. Properly indent multi-line strings and function arguments
6. Use consistent indentation throughout the codebase
7. Properly indent docstrings and comments
8. Use proper indentation for try/except blocks
9. Properly indent class methods and their contents