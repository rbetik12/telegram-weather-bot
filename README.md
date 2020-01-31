# Telegram weather bot

That bot can show you current weather in your location or a forecast for the next day. Bot caches your location and saves it in database, so it won't be lost and you don't need to set it manually every time.

## Launch prerequisites:
* Python 3.7 *(version can be lower, tested exactly on 3.7)*
* MongoDB instance installed locally
## Launch guide
First you should install dependecies through *pip*.
```Shell
$ pip install requirements.txt 
```
Then you should launch MongoDB instance.
```Shell
$ service mongod start
```
After that simply launch bot, but don't forget to set your Telegram API key in main.py
```Shell
$ python3 src/main.py
```
