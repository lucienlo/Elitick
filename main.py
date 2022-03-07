import json
import os, threading
from decimal import *

import shioaji as sj
import pandas as pd
from shioaji import BidAskSTKv1, Exchange

from src.auth import auth
from src.utils import logger as log

from src.test import ut_bidask


def subscribe_bidAsk(api, sid):
  api.quote.subscribe(
    api.Contracts.Stocks[sid], 
    quote_type = sj.constant.QuoteType.BidAsk,
    version = sj.constant.QuoteVersion.v1,
    intraday_odd = True
  )
  api.quote.subscribe(
    api.Contracts.Stocks[sid],
    quote_type = sj.constant.QuoteType.BidAsk,
    version = sj.constant.QuoteVersion.v1,
    intraday_odd = False
  )

def canEarn(buy, sell, amount, discount):
  fee = Decimal(0.001425)
  tax = Decimal(0.003)
  cost = ((sell * fee + buy * fee) * discount + sell * tax) * amount
  earn = (sell - buy) * amount
  return earn - cost

def quote_callback(exchange: Exchange, bidask:BidAskSTKv1):
  if bidask.intraday_odd == 1:
    global cur_bid_price
    global cur_bid_amount
    cur_bid_price = bidask.bid_price[0]
    cur_bid_amount = bidask.diff_bid_vol[0]
  else:
    global cur_ask_price
    global cur_ask_amount
    cur_ask_price = bidask.ask_price[0]
    cur_ask_amount = bidask.diff_ask_vol[0]

  if canEarn(cur_bid_price, cur_ask_price, 1000, 0.65) > 0 and cur_ask_amount >= 10000 and cur_bid_amount >= 100 :
    log.fatal('--- buy now ---, buy entire: ' + str(buy) + ', sell odd: ' + str(sell))

  log.info('Exchange: ' + str(exchange) + ', BidAsk: ' + str(bidask))


def main():
  handle = auth.login()

  odd_ba = subscribe_bidAsk(handle, "2330")
  handle.quote.set_on_bidask_stk_v1_callback(quote_callback)

  log.info("all setting done, it's listening...")
  threading.Event().wait()

  logout(handle)


def mock_ut():
  odd_ba = ut_bidask.get_mock_object(isOdd = True)
  entire_ba = ut_bidask.get_mock_object(isOdd = False)
  buy = entire_ba.ask_price[0]
  sell = odd_ba.bid_price[0]
  benifit = canEarn(buy, sell, 1000, Decimal(0.65))
  log.info('buy entire: ' + str(buy) + ', sell odd: ' + str(sell) + ', can earn: '+ str(benifit))
  if benifit > 0:
    log.info(' --- buy now --- ')

if __name__ == "__main__":
  main()
  #mock_ut()
