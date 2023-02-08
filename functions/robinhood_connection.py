import robin_stocks as rs
from dotenv import load_dotenv
import os 

robinhood_username = os.environ.get('ROBINHOOD_USERNAME')
robinhood_password = os.environ.get('ROBINHOOD_PASSWORD')
load_dotenv() 


def login():
    rs.robinhood.login(username=robinhood_username, password=robinhood_password, expiresIn=86400, by_sms=True)