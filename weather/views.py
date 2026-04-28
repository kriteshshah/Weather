import requests
from django.shortcuts import render
from django.conf import settings


def get_weather_icon_class(condition):
    condition = condition.lower()
    if 'clear' in condition:
        return 'clear'
    elif 'cloud' in condition:
        return 'cloudy'
    elif 'rain' in condition or 'drizzle' in condition:
        return 'rainy'
    elif 'thunder' in condition or 'storm' in condition:
        return 'stormy'
    elif 'snow' in condition:
        return 'snowy'
    elif 'mist' in condition or 'fog' in condition or 'haze' in condition:
        return 'foggy'
    return 'clear'


def index(request):
    context = {
        'weather': None,
        'forecast': None,
        'error': None,
        'city': '',
    }

    city = request.GET.get('city', '').strip()
    if not city and request.method == 'GET' and 'city' not in request.GET:
        city = 'London'  # Default city on first load

    if city:
        context['city'] = city
        api_key = settings.OPENWEATHER_API_KEY

        if api_key == 'YOUR_API_KEY_HERE':
            context['error'] = "⚠️ Please add your OpenWeatherMap API key in weatherapp/settings.py"
            return render(request, 'weather/index.html', context)

        # Current weather
        weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
        # 5-day forecast
        forecast_url = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric'

        try:
            weather_resp = requests.get(weather_url, timeout=10)
            forecast_resp = requests.get(forecast_url, timeout=10)

            if weather_resp.status_code == 404:
                context['error'] = f'City "{city}" not found. Please check the spelling.'
                return render(request, 'weather/index.html', context)

            if weather_resp.status_code == 401:
                context['error'] = 'Invalid API key. Please check your OpenWeatherMap API key.'
                return render(request, 'weather/index.html', context)

            weather_resp.raise_for_status()
            wd = weather_resp.json()

            weather = {
                'city': wd['name'],
                'country': wd['sys']['country'],
                'temp': round(wd['main']['temp']),
                'feels_like': round(wd['main']['feels_like']),
                'temp_min': round(wd['main']['temp_min']),
                'temp_max': round(wd['main']['temp_max']),
                'humidity': wd['main']['humidity'],
                'pressure': wd['main']['pressure'],
                'visibility': round(wd.get('visibility', 0) / 1000, 1),
                'wind_speed': round(wd['wind']['speed'] * 3.6, 1),  # m/s to km/h
                'wind_deg': wd['wind'].get('deg', 0),
                'description': wd['weather'][0]['description'].title(),
                'icon': wd['weather'][0]['icon'],
                'icon_class': get_weather_icon_class(wd['weather'][0]['main']),
                'sunrise': wd['sys']['sunrise'],
                'sunset': wd['sys']['sunset'],
                'cloudiness': wd['clouds']['all'],
            }
            context['weather'] = weather

            # Forecast — pick one reading per day (noon)
            if forecast_resp.status_code == 200:
                fd = forecast_resp.json()
                daily = {}
                for item in fd['list']:
                    date_str = item['dt_txt'].split(' ')[0]
                    time_str = item['dt_txt'].split(' ')[1]
                    if date_str not in daily and time_str == '12:00:00':
                        daily[date_str] = {
                            'date': date_str,
                            'temp_max': round(item['main']['temp_max']),
                            'temp_min': round(item['main']['temp_min']),
                            'description': item['weather'][0]['description'].title(),
                            'icon': item['weather'][0]['icon'],
                            'icon_class': get_weather_icon_class(item['weather'][0]['main']),
                            'humidity': item['main']['humidity'],
                            'wind': round(item['wind']['speed'] * 3.6, 1),
                        }
                # Fallback: if no noon entries, take first entry per day
                if not daily:
                    for item in fd['list']:
                        date_str = item['dt_txt'].split(' ')[0]
                        if date_str not in daily:
                            daily[date_str] = {
                                'date': date_str,
                                'temp_max': round(item['main']['temp_max']),
                                'temp_min': round(item['main']['temp_min']),
                                'description': item['weather'][0]['description'].title(),
                                'icon': item['weather'][0]['icon'],
                                'icon_class': get_weather_icon_class(item['weather'][0]['main']),
                                'humidity': item['main']['humidity'],
                                'wind': round(item['wind']['speed'] * 3.6, 1),
                            }

                context['forecast'] = list(daily.values())[:5]

        except requests.exceptions.ConnectionError:
            context['error'] = 'Network error. Please check your internet connection.'
        except requests.exceptions.Timeout:
            context['error'] = 'Request timed out. Please try again.'
        except Exception as e:
            context['error'] = f'Something went wrong: {str(e)}'

    return render(request, 'weather/index.html', context)
