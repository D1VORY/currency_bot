import datetime
import re
import os
from telegram.ext import  CallbackContext
from telegram.update import Update

from documents import UserExchangeData
from utils import  (
    beatify_rates, 
    get_current_rates, 
    parse_exchange, 
    ParsingException, 
    get_currency_pair_plot, 
    parse_history
)

def start(update: Update, context: CallbackContext):
    """
    hello world
    """
    text = """
    Hello this bot can show you current exhange rates!
    available commands:
    /list
    /exhange
    /history
    /change_base                   
    """
    update.message.reply_text(text)


def currency_list(update: Update, context: CallbackContext):
    """
    returns list of all available rates
    """
    rates = get_current_rates(update.message.chat_id)

    text = beatify_rates(rates)
    update.message.reply_text(text)


def exchange(update: Update, context: CallbackContext):
    """
    returns exchanged currency by the current price
    """
    rates = get_current_rates(update.message.chat_id)
    exchange_text = update.message.text

    try:
        usd_amount, target_currency = parse_exchange(exchange_text)
        converted = float(usd_amount) * rates[target_currency]
        update.message.reply_text(f"It's {round(converted,2)} {target_currency}")
    except (ParsingException, KeyError) as e:
        update.message.reply_text('Sorry, I did not understand.\n Try again')

    
def history(update: Update, context: CallbackContext):
    """
    returns an image graph chart which shows the exchange rate graph/chart
    of the selected currency for the last 7 days.
    """
    #update.message.reply_text('Sorry, I did not understand.\n Try again')
    #update.message.reply_photo(photo=open('soup.jpg', 'rb'))
    #I tried t make this asynchrnous, but it didn't work

    history_text = update.message.text

    try:
        base_currency, selected_currency, start_date, end_date = parse_history(history_text)
        print(base_currency, selected_currency, start_date, end_date)

    except (ParsingException, KeyError) as e:
        update.message.reply_text('Sorry, I did not understand.\n Try again')
    else:
        filename =  get_currency_pair_plot(base_currency, selected_currency,
                                    start_date , end_date 
                                    )
        update.message.reply_photo(photo=open(filename, 'rb'))
        os.remove(filename)

def soup(update, context):
    """Echo the user message."""
    update.message.reply_photo(photo=open('soup.jpg', 'rb'))


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

