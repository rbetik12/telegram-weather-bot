# Telegram weather bot

That bot can show you current weather in your location or a forecast for the next day. Bot caches your location and saves it in database, so it won't be lost and you don't need to set it manually every time.
Bot uses [OpenWeather API](https://openweathermap.org/api) to obtain weather info.
## Launch prerequisites:
* Python 3.7 *(version can be lower, tested exactly on 3.7)*
* MongoDB instance installed locally
## Launch guide
First you should install dependencies through *pip*.
```Shell
$ pip install requirements.txt 
```
Then you should launch MongoDB instance.
```Shell
$ service mongod start
```
After that simply launch bot, but don't forget to set your Telegram API key and OpenWeather API key in .config file. That file should be located in root folder.
```Shell
$ python3 src/main.py
```
