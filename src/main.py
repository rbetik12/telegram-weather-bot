import telebot
import requests
import json
import datetime
from pymongo import MongoClient
from typing import Union

with open('../.config') as config:
    lines = config.readlines()
    telegram_key, weather_key = lines[0].strip(), lines[1].strip()

db_client = MongoClient()
db = db_client.tgbot
user_geo_info_db = db.user_info

bot = telebot.TeleBot(telegram_key)
WEATHER_API_KEY = weather_key

send_location_button_text = 'Set your location'
get_weather_button_text = 'Get current weather'
get_forecast_button_text = 'Get forecast for one day'

keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

send_location_button = telebot.types.KeyboardButton(send_location_button_text, request_location=True)
get_weather_button = telebot.types.KeyboardButton(get_weather_button_text)
get_forecast_button = telebot.types.KeyboardButton(get_forecast_button_text)

keyboard.add(send_location_button)
keyboard.add(get_weather_button)
keyboard.add(get_forecast_button)

cached_user_geo_info = dict()


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Hey, mate, here you can get weather in your location or even a forecast!🌕',
                     reply_markup=keyboard)


@bot.message_handler(content_types=['location'])
def send_location(message):
    user_id = message.from_user.id
    cached_user_geo_info[user_id] = message.location
    message_str = str(message.location).replace('\'', '"')
    if user_geo_info_db.find_one({'user_id': user_id}) is None:
        user_geo_info_db.insert_one({'user_id': user_id, 'location': message_str})
    else:
        user_geo_info_db.update_one({'user_id': user_id}, {'$set': {'location': message_str}})
    bot.send_message(message.chat.id, 'Successfully set new location!')


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text == get_weather_button_text:
        get_weather(message)
    elif message.text == get_forecast_button_text:
        get_forecast(message)


def get_weather(message):
    user_id = message.from_user.id
    location = check_location(user_id)
    if location is None:
        bot.send_message(message.chat.id, 'You must set you location first')
        return
    response = requests.get('http://api.openweathermap.org/data/2.5/weather?lat=%f&lon=%f&appid=%s' % (
        location.latitude, location.longitude, WEATHER_API_KEY))
    if response.status_code == 200:
        weather_data = response.content
        weather_data = json.loads(weather_data.decode('utf-8'))
        temperature = round(float(weather_data['main']['temp']) - 273.15, 3)
        bot.send_message(message.chat.id,
                         '<b>Location: %s</b>\nWeather: %s\nWeather description: %s\nTemperature: %s°C' % (
                             weather_data['name'], weather_data['weather'][0]['main'],
                             weather_data['weather'][0]['description'], temperature), parse_mode='html')
    else:
        bot.send_message(message.chat.id, 'Something went wrong, try again, please')


def get_forecast(message):
    user_id = message.from_user.id
    location = check_location(user_id)
    if location is None:
        bot.send_message(message.chat.id, 'You must set you location first')
        return
    response = requests.get('http://api.openweathermap.org/data/2.5/forecast?lat=%f&lon=%f&cnt=10&appid=%s' % (
        location.latitude, location.longitude, WEATHER_API_KEY))
    if response.status_code == 200:
        weather_data = response.content
        weather_data = json.loads(weather_data.decode('utf-8'))
        weather_data['list'] = weather_data['list'][len(weather_data['list']) - 1]
        temperature = round(float(weather_data['list']['main']['temp']) - 273.15, 3)
        weather = weather_data['list']['weather'][0]['main']
        weather_description = weather_data['list']['weather'][0]['description']
        location = weather_data['city']['name'] + ' ' + weather_data['city']['country']
        forecast_time = datetime.datetime.strptime(weather_data['list']['dt_txt'][0:10], '%Y-%m-%d').strftime(
            '%d-%m-%Y') + weather_data['list']['dt_txt'][10:]
        bot.send_message(message.chat.id,
                         '<b>Forecast for %s</b>\n<i>Location: %s</i>\nWeather: %s\nWeather Description: '
                         '%s\nTemperature: %s°C' % (
                             forecast_time, location, weather, weather_description, temperature), parse_mode='html')
    else:
        print(response.status_code)
        bot.send_message(message.chat.id, 'Something went wrong, try again, please')


def check_location(user_id) -> Union[telebot.types.Location, None]:
    try:
        location = cached_user_geo_info[user_id]
        return location
    except KeyError:
        user_location_db = user_geo_info_db.find_one({'user_id': user_id})
        if user_location_db is None:
            return None
        else:
            location_dict = json.loads(user_location_db['location'])
            location = telebot.types.Location(location_dict['longitude'], location_dict['latitude'])
            cached_user_geo_info[user_id] = location
            return location


bot.polling()
