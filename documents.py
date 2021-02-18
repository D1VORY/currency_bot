from mongoengine import Document, DateTimeField, DictField, IntField
import datetime


class UserExchangeData(Document):
    timestamp = DateTimeField(default = datetime.datetime.now, required=True)
    rates = DictField(required=True)
    chatId = IntField(required=True)