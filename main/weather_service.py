import requests
import logging
from django.conf import settings
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WeatherService:
    """Service class for handling weather data from OpenWeather API"""
    
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = settings.OPENWEATHER_BASE_URL
        
    def get_current_weather(self, city_name, country_code=None):
        """Get current weather for a city (defaults to Harare, Zimbabwe)"""
        try:
            if country_code:
                location = f"{city_name},{country_code}"
            else:
                location = city_name
                
            url = f"{self.base_url}/weather"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric'  # Get temperature in Celsius
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'success': True,
                'data': {
                    'city': data['name'],
                    'country': data['sys']['country'],
                    'temperature': round(data['main']['temp']),
                    'feels_like': round(data['main']['feels_like']),
                    'humidity': data['main']['humidity'],
                    'pressure': data['main']['pressure'],
                    'description': data['weather'][0]['description'].title(),
                    'icon': data['weather'][0]['icon'],
                    'wind_speed': data['wind']['speed'],
                    'visibility': data.get('visibility', 0) / 1000,  # Convert to km
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching current weather: {str(e)}")
            return {
                'success': False,
                'error': f'Weather API error: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Unexpected error in get_current_weather: {str(e)}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def get_forecast(self, city_name, country_code=None, days=7):
        """Get weather forecast for a city (defaults to Harare, Zimbabwe)"""
        try:
            if country_code:
                location = f"{city_name},{country_code}"
            else:
                location = city_name
                
            url = f"{self.base_url}/forecast"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # 8 forecasts per day (every 3 hours)
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Process forecast data to get daily summaries
            daily_forecasts = self._process_forecast_data(data['list'], days)
            
            return {
                'success': True,
                'data': {
                    'city': data['city']['name'],
                    'country': data['city']['country'],
                    'forecast': daily_forecasts
                }
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching forecast: {str(e)}")
            return {
                'success': False,
                'error': f'Weather API error: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Unexpected error in get_forecast: {str(e)}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def _process_forecast_data(self, forecast_list, days):
        """Process raw forecast data into daily summaries"""
        daily_data = {}
        
        for item in forecast_list:
            date = datetime.fromtimestamp(item['dt']).date()
            
            if date not in daily_data:
                daily_data[date] = {
                    'date': date,
                    'temperatures': [],
                    'descriptions': [],
                    'icons': [],
                    'humidity': [],
                    'wind_speed': []
                }
            
            daily_data[date]['temperatures'].append(item['main']['temp'])
            daily_data[date]['descriptions'].append(item['weather'][0]['description'])
            daily_data[date]['icons'].append(item['weather'][0]['icon'])
            daily_data[date]['humidity'].append(item['main']['humidity'])
            daily_data[date]['wind_speed'].append(item['wind']['speed'])
        
        # Convert to list and calculate daily averages
        daily_forecasts = []
        today = datetime.now().date()
        
        for i, (date, data) in enumerate(sorted(daily_data.items())[:days]):
            avg_temp = round(sum(data['temperatures']) / len(data['temperatures']))
            min_temp = round(min(data['temperatures']))
            max_temp = round(max(data['temperatures']))
            
            # Get most common description and icon for the day
            most_common_desc = max(set(data['descriptions']), key=data['descriptions'].count)
            most_common_icon = max(set(data['icons']), key=data['icons'].count)
            
            avg_humidity = round(sum(data['humidity']) / len(data['humidity']))
            avg_wind = round(sum(data['wind_speed']) / len(data['wind_speed']), 1)
            
            # Determine day label
            if i == 0:
                day_label = "Today"
            elif i == 1:
                day_label = "Tomorrow"
            else:
                day_label = date.strftime("%a")
            
            daily_forecasts.append({
                'day': day_label,
                'date': date.isoformat(),
                'temperature': avg_temp,
                'min_temp': min_temp,
                'max_temp': max_temp,
                'description': most_common_desc.title(),
                'icon': most_common_icon,
                'humidity': avg_humidity,
                'wind_speed': avg_wind
            })
        
        return daily_forecasts
    
    def get_weather_alerts(self, city_name, country_code=None):
        """Get weather alerts and agricultural advice based on current conditions (defaults to Harare, Zimbabwe)"""
        try:
            current_weather = self.get_current_weather(city_name, country_code)
            
            if not current_weather['success']:
                return current_weather
            
            weather_data = current_weather['data']
            alerts = []
            irrigation_advice = self._generate_irrigation_advice(weather_data)
            
            # Temperature alerts
            if weather_data['temperature'] > 35:
                alerts.append({
                    'type': 'warning',
                    'icon': 'fas fa-thermometer-full',
                    'title': 'High Temperature Alert',
                    'message': 'Temperatures are very high. Consider increasing irrigation frequency and providing shade for sensitive crops.'
                })
            elif weather_data['temperature'] < 5:
                alerts.append({
                    'type': 'warning',
                    'icon': 'fas fa-thermometer-empty',
                    'title': 'Frost Alert',
                    'message': 'Low temperatures detected. Protect sensitive crops with covers or move them indoors.'
                })
            
            # Humidity alerts
            if weather_data['humidity'] > 80:
                alerts.append({
                    'type': 'info',
                    'icon': 'fas fa-tint',
                    'title': 'High Humidity',
                    'message': 'High humidity detected. Monitor for fungal diseases and ensure good air circulation.'
                })
            elif weather_data['humidity'] < 30:
                alerts.append({
                    'type': 'info',
                    'icon': 'fas fa-sun',
                    'title': 'Low Humidity',
                    'message': 'Low humidity detected. Consider increasing irrigation frequency.'
                })
            
            # Wind alerts
            if weather_data['wind_speed'] > 15:
                alerts.append({
                    'type': 'warning',
                    'icon': 'fas fa-wind',
                    'title': 'Strong Winds',
                    'message': 'Strong winds detected. Secure any loose structures and consider delaying pesticide applications.'
                })
            
            # Precipitation alerts (if available)
            if 'rain' in weather_data['description'].lower():
                alerts.append({
                    'type': 'info',
                    'icon': 'fas fa-cloud-rain',
                    'title': 'Rain Expected',
                    'message': 'Rain is expected. Consider delaying fertilizer application and harvesting activities.'
                })
            
            return {
                'success': True,
                'data': {
                    'alerts': alerts,
                    'current_weather': weather_data,
                    'irrigation_advice': irrigation_advice
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating weather alerts: {str(e)}")
            return {
                'success': False,
                'error': f'Error generating alerts: {str(e)}'
            }

    def _generate_irrigation_advice(self, weather_data):
        """Generate concise, actionable irrigation guidance for the day based on weather."""
        temp = weather_data.get('temperature')
        humidity = weather_data.get('humidity')
        wind = weather_data.get('wind_speed')
        desc = (weather_data.get('description') or '').lower()

        # Rain-first rule
        if 'rain' in desc or 'drizzle' in desc or 'shower' in desc:
            return (
                "Rain expected today—skip irrigation and leverage natural rainfall. "
                "Check drainage in low-lying areas and resume normal schedule tomorrow if soils dry."
            )

        # Temperature-driven guidance
        if temp is not None:
            if temp > 35:
                base = (
                    "Very hot conditions—irrigate early morning and/or late evening to reduce losses. "
                    "Increase frequency, use mulch to conserve moisture, and avoid midday irrigation."
                )
            elif 28 < temp <= 35:
                base = (
                    "Hot day—maintain schedule and consider a short top‑up cycle this evening. "
                    "Prioritize deep, infrequent watering over light sprinkles."
                )
            elif 18 <= temp <= 28:
                base = (
                    "Mild conditions—follow your normal schedule. Irrigate in the morning for best uptake."
                )
            elif 5 <= temp < 18:
                base = (
                    "Cool day—reduce irrigation frequency by ~20–30%. Water mid‑morning if needed to avoid overnight wet soils."
                )
            else:  # temp < 5
                base = (
                    "Frost risk—avoid irrigation overnight and early morning. Only water at midday if soil is dry and plants show stress."
                )
        else:
            base = "Follow your normal schedule and check soil moisture before watering."

        # Humidity modifiers
        modifiers = []
        if humidity is not None:
            if humidity > 80:
                modifiers.append("High humidity—watch for fungal disease; avoid late‑evening watering.")
            elif humidity < 30:
                modifiers.append("Very dry air—check moisture more often and ensure adequate mulching.")

        # Wind modifiers
        if wind is not None and wind > 15:
            modifiers.append("Strong winds—use drip/low‑angle sprinklers and shield young plants.")

        if modifiers:
            return base + " " + " ".join(modifiers)
        return base

# Global instance
weather_service = WeatherService()
