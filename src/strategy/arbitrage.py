# pip installed
from shioaji import BidAskSTKv1, Exchange

# local
from src.utils import logger as log
from src.connection import register

# python STL
from decimal import *

# global varible
g_sell = None
g_buy = None

ERAN_TARGET = Decimal(0)

TRADE_FEE = Decimal(0.001425)
TRADE_TAX = Decimal(0.003)
DISCOUNT = Decimal(0.65)

SELL_FEE = TRADE_FEE * DISCOUNT + TRADE_TAX
BUY_FEE = TRADE_FEE * DISCOUNT

def calculate(buy:Decimal, sell:Decimal, amount:int):
  cost = sell * SELL_FEE + buy * BUY_FEE
  earn = sell - buy
  return (earn - cost) * amount
  return earn - cost

def order_cb(result):
  log.fatal('TO-DO: order_cb not implement yet')


def action(id: str, buy_price: int, sell_price: int, amount: int):
  if register.set_sell_order(2330, buy_price, 999, order_cb) == 'Complete':
  	return register.set_buy_order(2330, sell_price, 1000, , order_cb) == 'Complete'

  return False

def vaild(benifit, want):
  return benifit <= want and g_sell.ask_volume[0] < g_buy.ask_volume[0] * 2000

def try_earn(want: Decimal):
  global g_sell
  global g_buy

  if g_sell == None or g_buy == None:
    log.warning('not complete set \'sell\' or \'buy\' component')
    return False

  benifit = calculate(g_buy.ask_price[0], g_sell.ask_price[0], 1000)
  log.info('buy entire: ' + str(g_buy.ask_price[0]) + '(' + str(g_buy.ask_volume[0]) + '), ' +
           'sell odd: ' + str(g_sell.ask_price[0]) + '(' + str(g_sell.ask_volume[0]) + '), ' +
           'can earn: '+ str(benifit))

  if benifit <= want and g_sell.ask_volume[0] < g_buy.ask_volume[0] * 2000: #to do, judgement whether can action.
    return False

  return action('2330', g_buy.ask_price[0], g_sell.ask_price[0], 1000)
  # return True

def update(bidask:BidAskSTKv1):
  global g_sell
  global g_buy

  if bidask.intraday_odd == 1:
  	g_sell = bidask
  else:
    g_buy = bidask

  log.toObj(bidask)
  try_earn(ERAN_TARGET)
