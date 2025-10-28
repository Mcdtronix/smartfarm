# Weather API Setup Instructions

## OpenWeather API Integration

Your SmartFarm application now includes real-time weather data integration using the OpenWeather API. Here's how to set it up:

### 1. Get Your OpenWeather API Key

1. Go to [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Navigate to the API keys section
4. Copy your API key

### 2. Configure Your API Key

1. Open `farmsmart_project/settings.py`
2. Find the line: `OPENWEATHER_API_KEY = 'YOUR_OPENWEATHER_API_KEY_HERE'`
3. Replace `YOUR_OPENWEATHER_API_KEY_HERE` with your actual API key
4. Save the file

### 3. Install Required Dependencies

Run this command to install the requests library:

```bash
pip install requests
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

### 4. Test the Integration

1. Start your Django server: `python manage.py runserver`
2. Navigate to your homepage
3. Scroll down to the "Weather Alerts & Seasonal Planning" section
4. You should see real weather data loading

### 5. API Endpoints Available

- `/api/weather/current/?city=Harare&country=ZW` - Current weather
- `/api/weather/forecast/?city=Harare&days=7` - 7-day forecast
- `/api/weather/alerts/?city=Harare` - Weather alerts and agricultural advice

### 6. Features Included

- **Real-time Weather Data**: Current temperature, humidity, wind speed
- **7-Day Forecast**: Daily weather predictions with icons
- **Agricultural Alerts**: Smart alerts based on weather conditions
- **Location Support**: Uses the location from your farm form or defaults to Harare, Zimbabwe
- **Error Handling**: Graceful fallback if API is unavailable

### 7. Customization

You can customize the default location by modifying the default values in:

- `main/views.py` (lines 306, 331, 357) - Change 'Harare' to your preferred city
- `static/js/main.js` (lines 167, 209) - Change 'Harare' to your preferred city

### 8. Free Tier Limits

The free OpenWeather API tier includes:

- 1,000 API calls per day
- Current weather and 5-day forecast
- Perfect for development and small-scale use

For production use with higher traffic, consider upgrading to a paid plan.
