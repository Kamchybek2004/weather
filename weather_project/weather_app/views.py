from django.shortcuts import render
import requests
from datetime import datetime  # Для форматирования времени
from .models import City
from .forms import CityForm

def format_unix_time(unix_time):
    """Преобразование UNIX времени в формат ЧЧ:ММ:СС."""
    return datetime.fromtimestamp(unix_time).strftime('%H:%M:%S')

def get_weather_data(request):
    url = "http://api.openweathermap.org/data/2.5/weather"
    cities = City.objects.all()
    error_messages = []
    weather_details = []
    error_message = None

    if(request.method == "POST"):
        form = CityForm(request.POST)
        form.save()

    form = CityForm()


    for city_obj in cities:
        city_name = city_obj.name

        params = {
            "q": city_name,
            "appid": "c7af500b96b381f1c8085e9f3d18ca04",
            "units": "metric",
            "lang": "ru"
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            weather_data = response.json()

            # Извлекаем данные, если ответ успешен
            if weather_data.get("cod") == 200:  # Проверяем успешный код ответа
                weather_details.append({
                    "temperature": weather_data['main']['temp'],
                    "feels_like": weather_data['main']['feels_like'],
                    "humidity": weather_data['main']['humidity'],
                    "wind_speed": weather_data['wind']['speed'],
                    "description": weather_data['weather'][0]['description'],
                    "sunrise": format_unix_time(weather_data['sys']['sunrise']),
                    "sunset": format_unix_time(weather_data['sys']['sunset']),
                    "city": weather_data['name'],
                    "country": weather_data['sys']['country'],
                    "icon": weather_data['weather'][0]['icon']
                })
            else:
                error_messages.append(f"Ошибка для города {city_name}: {weather_data.get('message', 'Неизвестная ошибка')}")
        except requests.exceptions.RequestException as e:
            error_messages.append(f"Ошибка соединения для города {city_name}: {e}")
        except Exception as e:
            error_messages.append(f"Произошла ошибка для города {city_name}: {e}")

    context = {
        "cities_weather_data": weather_details if not error_message else None,
        "error_messages": error_messages,
        "form": form
    }

    return render(request, 'index.html', context)
