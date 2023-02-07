from datetime import datetime, timedelta
import robin_stocks as rs
from robinhood_connection import login
from FIFO_tax_queue import Trans, balanceFifo
login()


ticker = 'VOO'
current_share_price = round(float(rs.robinhood.stocks.get_latest_price(ticker)[0]), 2)
current_quantity = float(rs.robinhood.account.build_holdings()[ticker]['quantity'])
# current_share_price = 376.21 # use these to speed up testing
# current_quantity = 103.256713
orders = rs.robinhood.orders.find_stock_orders(symbol=ticker, cancel=None)
orders.reverse()


def enque_orders(orders):
    trans_list = list()

    for order in orders:
        if order['state'] != 'cancelled':
            order_date = str(datetime.strptime(order['updated_at'][:10], '%Y-%m-%d'))[:10]
            price = round(float(order['average_price']), 2)
            num_shares = round(float(order['cumulative_quantity']), 6)
            if order['side'] == 'buy':
                trans = Trans(order_date, num_shares, price)
            elif order['side'] == 'sell':
                trans = Trans(order_date, -1.0 * num_shares, price)
            trans_list.append(trans)
    return trans_list

# print("Processed", len(trans_list), "buy and sell orders (including dividend reinvestment, and conditional orders) for", ticker)

lt_shares_dict = {}
lt_shares_min = 0
for i in range(365):
    # get the date one day in the future
    date = datetime.now() + timedelta(days=i)
    tax_queue = enque_orders(orders)
    lt_shares, st_shares = balanceFifo(tax_queue, current_share_price, current_date=date)
    if lt_shares > lt_shares_min:
        # lt_shares_min = lt_shares
        lt_shares_dict[str(date)[:10]] = lt_shares
        lt_shares_min = lt_shares
    # get the number of shares currently held in the account for VOO
    assert round(lt_shares + st_shares, 6) == round(current_quantity, 6) # lt+st shares should always equal total shares
    tax_queue.clear()

# shows the number of shares you can sell under long-term tax rates as they become available. Last entry should never be more than a year into the future.
print(lt_shares_dict)