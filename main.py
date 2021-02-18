import requests
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.update import Update
from mongoengine import connect
import logging
from dotenv import load_dotenv

from handlers import start, echo, currency_list, exchange, history, soup
load_dotenv()


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


TOKEN = os.getenv('TELEGRAM_TOKEN')
#TODO replace it with env value


def main():
    """
    Bot initialization
    """
    #db password 
    #try to connect to db
    connect(
        name = os.getenv('DB_NAME'),
        host = os.getenv('DB_HOST'))

    updater = Updater(token=TOKEN, use_context=True)

    dispathcer = updater.dispatcher


    #TODO make available list of all commands or make buttons
    dispathcer.add_handler(CommandHandler('start', start))
    dispathcer.add_handler(CommandHandler('list', currency_list))
    dispathcer.add_handler(CommandHandler('exchange', exchange))
    dispathcer.add_handler(CommandHandler('history', history, run_async=True))
    dispathcer.add_handler(CommandHandler('soup', soup))
    # on noncommand i.e message - echo the message on Telegram
    dispathcer.add_handler(MessageHandler(Filters.text, echo))


     # log all errors
    dispathcer.add_error_handler(error)


    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    

    main()