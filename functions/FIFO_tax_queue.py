import logging
from collections import deque
import math
from datetime import datetime, timedelta

class Trans:
    datetime = None
    amount = None
    price = None

    def __init__(self, datetime, amount, price):
        self.datetime = datetime
        self.amount = amount
        self.price = price

    def getInfo(self):
        return (str(self.datetime) + "; " +
                str(self.amount) + "; " +
                str(self.price)) + "; "


def balanceFifo(all_trans, current_share_price, current_date=datetime.now(), holding_period=365, verbose=False):
    qTransactions = deque()

    for t in all_trans:
        t.amount = round(t.amount, 6)
        # Add first element to the queue
        if len(qTransactions) == 0:
            logging.debug('Added the first element: %s', t.getInfo())
            qTransactions.append(t)
            continue

        while t.amount != 0 and len(qTransactions) > 0:
            # investigate the first element from the queue
            tq = qTransactions.popleft()
            tq.amount = round(tq.amount, 6)
            # the same type of transaction: both sell or both buy
            if tq.amount * t.amount > 0:
                # return the first element back to the same place
                qTransactions.appendleft(tq)
                # add the new element to the list
                qTransactions.append(t)
                logging.debug('Added: %s', t.getInfo())
                break

            # contrary transactions: (sell and buy) or (buy and sell)
            if tq.amount * t.amount < 0:
                logging.debug('Transaction : %s', t.getInfo())
                logging.debug('... try to balance with: %s', tq.getInfo())

                # The element in the queue have more units and takes in the current transaction
                if abs(tq.amount) > abs(t.amount):
                    insertTransaction(tq.datetime, t.datetime, math.copysign(t.amount, tq.amount), tq.price, t.price, verbose)
                    # update the amount of the element in the queue
                    tq.amount = round(tq.amount + t.amount, 6)
                    # return the element back to the same place
                    qTransactions.appendleft(tq)
                    logging.debug('Removed transaction: %s', t.getInfo())
                    # the transaction has been balanced, take a new transaction
                    break

                # The element from the queue and transaction have the same amount of units
                if abs(tq.amount) == abs(t.amount):
                    insertTransaction(tq.datetime, t.datetime, math.copysign(t.amount, tq.amount), tq.price, t.price, verbose)

                    # update the amount in the transaction
                    t.amount = 0
                    logging.debug('Balanced, removed transaction: %s', t.getInfo())
                    logging.debug('Balanced, removed from the queue: %s', tq.getInfo())
                    # the transaction has been balanced, take a new transaction
                    continue
                # The transaction has more units
                if abs(tq.amount) < abs(t.amount):
                    # update the units in transaction, (remove element from the queue)
                    t.amount = round(t.amount + tq.amount, 6)
                    insertTransaction(tq.datetime, t.datetime, tq.amount, tq.price, t.price, verbose)
                    logging.debug('Removed from queue: %s', tq.getInfo())

                    # the transaction has not been balanced,
                    # take a new element from the queue (t.amount>0)
                    continue

        # We have unbalanced transaction but the queue is empty
        if t.amount != 0 and len(qTransactions) == 0:
            # Add unbalanced transaction to the queue
            # The queue changes polarisation
            qTransactions.append(t)
            logging.debug('Left element: %s', t.getInfo())

    # If something remained in the queue, treat it as open or part-open transactions
    num_long_term_shares = 0
    num_short_term_shares = 0
    while len(qTransactions) > 0:
        tq = qTransactions.popleft()
        if verbose:
            print('Remained on list transaction:', tq.getInfo())
        # for shares, date in purchase_history:
        holding_days = (current_date - datetime.strptime(tq.datetime, '%Y-%m-%d')).days
        if holding_days >= holding_period:
            num_long_term_shares += tq.amount
        else:
            num_short_term_shares += tq.amount

    num_long_term_shares = round(num_long_term_shares, 6)
    num_short_term_shares = round(num_short_term_shares, 6)
    if verbose:
        print("")
        print('Long term shares:', num_long_term_shares)
        print('Short term shares:', num_short_term_shares)
        print('Current share price:', current_share_price)
        print("You can sell up to {} dollars of shares paying long term capital gains rates".format(round(num_long_term_shares*current_share_price, 2)))
        print("Once you have sold all the long-term shares, you can sell up to {} dollars of shares paying short term capital gains rates".format(round(num_short_term_shares*current_share_price, 2)))
    return num_long_term_shares, num_short_term_shares

def insertTransaction(dateStart, dateEnd, amount, priceStart, priceEnd, verbose=False):
    if verbose:
        print("Bought={}, sold={},  amount={}, buy price={}, sell_price={}, gain={}".format(dateStart, dateEnd, amount, priceStart, priceEnd, round(amount * (priceEnd - priceStart), 6), 2))
