from flask_bcrypt import Bcrypt
from app.mongo import mongo
from app.models.Client import Client
import requests
from json import dumps
bcrypt = Bcrypt()

BASE_URL, HEADERS = Client.BASE_URL, Client.HEADERS


class Account:
    @staticmethod
    def format_account_data(account_type, account_name):
        """ format data for get oauth endpoint for SynapseFi API """
        data = {
            "type": account_type,
            "info": {
                "nickname": account_name,
                "document_id": "7fabc42b58d0a938f4780f09164baa3e7dbd27cef012d02181ece5bf5cf73dd5"
            }    
        }
        return data
    @staticmethod
    def format_transaction_data(to_account_type, to_account_id, amount):
        """ format data to create transaction for SynapseFi API """
        data = {
            "to": {
                "type": to_account_type,
                "id": to_account_id
            },
            "amount": {
                "amount": amount,
                "currency": "USD"
            },
            "extra": {
                "ip": "127.0.0.1",
                "note": "Test transaction"
            }
        }
        return data
