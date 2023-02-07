This lightweight system implements a FIFO queue for the purpose of optimising short and long term capital gains tax for a given
stock. It is designed to integrate directly with your robinhood account, pulling a full history of transactions for a given stock.

Ensure to run:
'''
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
'''

Also ensure to add your robinhood credentials to the .env file in the form:
'''
ROBINHOOD_USERNAME='...'
ROBINHOOD_PASSWORD='...'
'''

Then set the ticker symbol (default = 'VOO') in tax_optimisation.py, and run to see the results. The results are printed to the console, and give a schedule of when to sell your shares to minimise your tax bill.