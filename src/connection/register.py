# pip installed
import shioaji as sj
from shioaji import BidAskSTKv1, Exchange

# local
from src.utils import logger as log
from src.strategy import arbitrage as arbi

def bid_ask_entire_and_odd(handle, sid):
  handle.quote.subscribe(
    handle.Contracts.Stocks[sid], 
    quote_type = sj.constant.QuoteType.BidAsk,
    version = sj.constant.QuoteVersion.v1,
    intraday_odd = True
  )
  handle.quote.subscribe(
    handle.Contracts.Stocks[sid],
    quote_type = sj.constant.QuoteType.BidAsk,
    version = sj.constant.QuoteVersion.v1,
    intraday_odd = False
  )

def quote_callback(exchange: Exchange, bidask:BidAskSTKv1):
  arbi.update(bidask)

def start_watch_bid_ask(handle, isMock = False):
  if not isMock:
    handle.quote.set_on_bidask_stk_v1_callback(quote_callback)

def set_buy_order(info ,order_cb):
  isOdd = True

  log.fatal('TO-DO: register.set_order not implement yet')
  result = None
  order_cb(result)

def set_sell_order(info ,order_cb):
  log.fatal('TO-DO: register.set_order not implement yet')
  result = None
  order_cb(result)

def cancel_order(info ,order_cb):
  log.fatal('TO-DO: register.cancel_order not implement yet')
  result = None
  order_cb(result)
