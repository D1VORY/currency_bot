# Currency exchange bot

A telegram bot built with python, python-telegram-bot and MongoDB. Find it with @myCurrencyExch_bot


## Installation

1. install dependecies with 
```sh
pipenv install
```
2. activate environment
```sh
pipenv shell
```
2. Create a .env file with following fields:

| Variable | Value |
| ------ | ------ |
| TELEGRAM_TOKEN | Your telegram token |
| DB_HOST | Host uri of your MongoDB instace |
| DB_NAME | Name of database |

3. Start server with
```sh
python main.py
```
