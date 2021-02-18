from documents import UserExchangeData
import datetime
import requests
import json
import re
from typing import Tuple
import matplotlib
from matplotlib import pyplot as plt
import numpy
from random import randint

matplotlib.use('Agg')


def get_currency_pair_plot(base_currency:str, selected_currency:str, start_at, end_at):
    """
    returns a plot of currency pair history for 7 days
    """
    resp = requests.get(f'http://api.exchangeratesapi.io/history?start_at={start_at}&end_at={end_at}&base={base_currency}&symbols={selected_currency}')
    if resp.status_code != 200:
        raise ParsingException
    
    rates =  json.loads(resp.content)['rates']

    #parse resulted content to List[Tuple[date:str, value:float]]
    unsorted = list({key: rates[key][selected_currency] for key in rates}.items())
    sortedArr = numpy.sort(unsorted, axis = 0)
    
    x = sortedArr[:,0] #dates

    y = sortedArr[:,1] #values 

    
    plt.bar(x,y)
    fig = plt.gcf()
    fig.set_size_inches(10.8, 10.8)

    filename = f"images/{base_currency}|{selected_currency}_{datetime.datetime.now()}_{randint(0,1000)}.png"
    plt.savefig(filename, dpi= 100)
    return filename


def parse_history(text:str)->Tuple[str,str,str,str]:
    """
    parses history command and returns 
    base_currency, selected_currency, start date, end date
    """
    pattern = r'([A-Z]{3})\/([A-Z]{3})'
    matches = re.findall(pattern, text)
    print(matches)
    if not matches:
        raise ParsingException
    base_currency, selected_currency =  matches[0]

    today = datetime.datetime.now()
    end_date = str(today.date())
    start_date = str((today - datetime.timedelta(days=7)).date())

    return base_currency, selected_currency, start_date, end_date

def parse_exchange(exchange_text:str)->Tuple[int, str]:
    """
    returns dollar amount and target currency
    """
    pattern = r'^/exchange\D*(\d+).*(.{3}$)'
    matches = re.findall(pattern, exchange_text)

    if not matches:
        raise ParsingException

    usd_amount, target_currency = matches[0]
    return usd_amount, target_currency.upper()


def get_current_rates(chat_id:int)->dict:
    """
    returns current currency rates.
    if user requested anything from app within 10 minutes,
    data will be loaded from db,
    otherwise data will be loaded from api and updated
    """
    if not check_current_timestamp(chat_id):
        #print('got from db')
        rates = UserExchangeData.objects.get(chatId = chat_id).rates
    else:
        #print('got from api')
        api_response = requests.get('https://api.exchangeratesapi.io/latest?base=USD')
        if api_response.status_code != 200:
            #update.message.reply_text("Exchange rates server isn't responding.")
            return

        rates = json.loads(api_response.content)['rates']

        #create or update
        create_or_update_UserExchangeData(rates= rates, chat_id = chat_id)
    return rates


def beatify_rates(rates:dict)->str:
    """
    returns a beatified string from exchange rates dict 
    """
    text = '\n'.join(f"💸 {key}: {round(rates[key], 2)}" for key in rates)
    return 'current exchange rates are:\n' + text
    


def check_current_timestamp(chat_id:int)->bool:
    """
    Checks if difference between current datetime and
    timestamp retrieved from db for specific chat is bigger than 10 minutes 
    """
    try:
        data = UserExchangeData.objects.get(chatId = chat_id)

        #difference in minutes between current datetime and datetime saved in db
        diff = (datetime.datetime.now() - data.timestamp).total_seconds() / 60

        return diff > 10
            
    except UserExchangeData.DoesNotExist:
        return True
    except UserExchangeData.MultipleObjectsReturned:
        leave_last_entry(chat_id)
        return False


def create_or_update_UserExchangeData(chat_id:int, rates:dict):
    try:
        data = UserExchangeData.objects.get(chatId = chat_id)
        data.timestamp = datetime.datetime.now()
        data.rates = rates
        data.save()
    except UserExchangeData.DoesNotExist:
        #if such data isnt in db - proceed in creating it
        UserExchangeData(rates= rates, chatId = chat_id).save()
    except UserExchangeData.MultipleObjectsReturned:
        leave_last_entry(chat_id)


def leave_last_entry(chat_id:int):
    """
    deletes all entries from collection with a given chat_id 
    and leaves only last one 
    """
    temp = UserExchangeData.objects(chatId = chat_id).order_by('timestamp')
    temp[:(len(temp) -1 )].delete()

class ParsingException(Exception):
    """
    raised when text wasn't parsed correctly
    """