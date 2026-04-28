import requests
from datetime import datetime, timedelta, timezone
from django.shortcuts import render
from django.conf import settings


def _city_tzinfo(seconds_offset):
    return timezone(timedelta(seconds=int(seconds_offset)))


def _format_local_time(unix_ts, seconds_offset):
    utc = datetime.fromtimestamp(int(unix_ts), tz=timezone.utc)
    local = utc.astimezone(_city_tzinfo(seconds_offset))
    return local.strftime('%H:%M')


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
    elif 'mist' in condition or 'fog' in condition or 'haze' in condition or 'smoke' in condition:
        return 'foggy'
    return 'clear'


def _aqi_label(aqi):
    return {
        1: 'Good',
        2: 'Fair',
        3: 'Moderate',
        4: 'Poor',
        5: 'Very poor',
    }.get(aqi, 'Unknown')


def _forecast_by_local_day(forecast_list, seconds_offset):
    """Group 3-hour forecast rows by calendar date in the city's timezone."""
    tzinfo = _city_tzinfo(seconds_offset)
    days = {}
    for item in forecast_list:
        local = datetime.fromtimestamp(int(item['dt']), tz=timezone.utc).astimezone(tzinfo)
        key = local.strftime('%Y-%m-%d')
        tmin = item['main']['temp_min']
        tmax = item['main']['temp_max']
        if key not in days:
            days[key] = {
                'date': key,
                'temp_max': tmax,
                'temp_min': tmin,
                'description': item['weather'][0]['description'].title(),
                'icon': item['weather'][0]['icon'],
                'icon_class': get_weather_icon_class(item['weather'][0]['main']),
                'humidity': item['main']['humidity'],
                'wind': round(item['wind']['speed'] * 3.6, 1),
            }
        else:
            agg = days[key]
            agg['temp_max'] = max(agg['temp_max'], tmax)
            agg['temp_min'] = min(agg['temp_min'], tmin)
    for agg in days.values():
        agg['temp_max'] = round(agg['temp_max'])
        agg['temp_min'] = round(agg['temp_min'])
    return days


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

        weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
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

            tz_offset = int(wd.get('timezone', 0))
            tzinfo = _city_tzinfo(tz_offset)
            today_key = datetime.fromtimestamp(int(wd['dt']), tz=timezone.utc).astimezone(tzinfo).strftime('%Y-%m-%d')

            daily_by_date = {}
            if forecast_resp.status_code == 200:
                fd = forecast_resp.json()
                daily_by_date = _forecast_by_local_day(fd['list'], tz_offset)

            # True daily range from 3-hour forecast; current API often repeats min/max.
            day_range = daily_by_date.get(today_key)
            if day_range:
                display_min = day_range['temp_min']
                display_max = day_range['temp_max']
            else:
                display_min = round(wd['main']['temp_min'])
                display_max = round(wd['main']['temp_max'])

            lat = wd['coord']['lat']
            lon = wd['coord']['lon']
            aqi_value = None
            aqi_label = None
            aq_resp = requests.get(
                f'https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}',
                timeout=10,
            )
            if aq_resp.status_code == 200:
                payload = aq_resp.json()
                if payload.get('list'):
                    aqi_value = int(payload['list'][0]['main']['aqi'])
                    aqi_label = _aqi_label(aqi_value)

            sys_info = wd.get('sys') or {}
            sr = sys_info.get('sunrise')
            ss = sys_info.get('sunset')
            weather = {
                'city': wd['name'],
                'country': sys_info.get('country', ''),
                'temp': round(wd['main']['temp']),
                'feels_like': round(wd['main']['feels_like']),
                'temp_min': display_min,
                'temp_max': display_max,
                'humidity': wd['main']['humidity'],
                'pressure': wd['main']['pressure'],
                'visibility': round(wd.get('visibility', 0) / 1000, 1),
                'wind_speed': round(wd.get('wind', {}).get('speed', 0) * 3.6, 1),  # m/s to km/h
                'wind_deg': wd.get('wind', {}).get('deg', 0),
                'description': wd['weather'][0]['description'].title(),
                'icon': wd['weather'][0]['icon'],
                'icon_class': get_weather_icon_class(wd['weather'][0]['main']),
                'sunrise_local': _format_local_time(sr, tz_offset) if sr is not None else '—',
                'sunset_local': _format_local_time(ss, tz_offset) if ss is not None else '—',
                'cloudiness': wd['clouds']['all'],
                'aqi': aqi_value,
                'aqi_label': aqi_label,
            }
            context['weather'] = weather

            if daily_by_date:
                ordered_dates = sorted(daily_by_date.keys())[:5]
                context['forecast'] = [daily_by_date[d] for d in ordered_dates]

        except requests.exceptions.ConnectionError:
            context['error'] = 'Network error. Please check your internet connection.'
        except requests.exceptions.Timeout:
            context['error'] = 'Request timed out. Please try again.'
        except Exception as e:
            context['error'] = f'Something went wrong: {str(e)}'

    return render(request, 'weather/index.html', context)
