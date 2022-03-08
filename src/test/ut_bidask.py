from shioaji import BidAskSTKv1, Exchange

import datetime
from decimal import *

def get_mock_object(isOdd = False):
  if isOdd:
    return BidAskSTKv1(
      code = '2330',
      datetime = datetime.datetime(2021, 7, 2, 13, 17, 45, 743299),
      bid_price = [Decimal('593'), Decimal('592'), Decimal('591'), Decimal('590'), Decimal('589')], 
      bid_volume = [59391, 224490, 74082, 68570, 125246], 
      diff_bid_vol = [49874, 101808, 23863, 38712, 77704], 
      ask_price = [Decimal('594'), Decimal('595'), Decimal('596'), Decimal('597'), Decimal('598')], 
      ask_volume = [26355, 9680, 18087, 11773, 3568], 
      diff_ask_vol = [13251, -14347, 39249, -20397, -10591], 
      suspend = 0, 
      simtrade = 1, 
      intraday_odd = 1
    )
  else:
  	return BidAskSTKv1(
      code = '2330', 
      datetime = datetime.datetime(2021, 7, 1, 9, 9, 54, 36828), 
      bid_price = [Decimal('589'), Decimal('588'), Decimal('587'), Decimal('586'), Decimal('585')], 
      bid_volume = [248, 180, 258, 267, 163], 
      diff_bid_vol = [3, 0, 0, 0, 0], 
      ask_price = [Decimal('590'), Decimal('591'), Decimal('592'), Decimal('593'), Decimal('594')],
      ask_volume = [1457, 531, 506, 90, 259], 
      diff_ask_vol = [0, 0, 0, 0, 0], 
      suspend = 0, 
      simtrade = 0,
      intraday_odd = 0
    )


def trade():
  log.fatal('TO-DO: set_order not implement yet')
#TO-DO
	# contract = api.Contracts.Stocks.TSE.TSE2330
 #    order = api.Order(price=12,
 #                  quantity=10,
 #                  action=sj.constant.Action.Buy,
 #                  price_type=sj.constant.StockPriceType.LMT,
 #                  order_type=sj.constant.TFTOrderType.ROD,
 #                  account=api.stock_account
 #                  )
 #    trade = api.place_order(contract, order)