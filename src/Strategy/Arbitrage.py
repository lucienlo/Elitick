# python STL
from decimal import *
import time

# pip installed
from shioaji import BidAskSTKv1, Exchange

# local
from src.Utils.Logger import Logger
from src.Core.Register import *

class Arbitrage:
  def __init__(self, monitor, trade_fee: Decimal= Decimal(0.001425), trade_tax: Decimal = Decimal(0.003), \
                     fee_discount: Decimal = Decimal(0.65), target_benifit: float = 0):
    self.log = Logger(self.__class__.__name__)
    #static value
    self.safe_entire_odd_ratio = 2
    self.safe_entire_quantity = 100
    self.trade_entire_quantity = 1
    self.trade_odd_quantity = 999

    self.monitor = monitor

    self.target_benifit = target_benifit
    self.sell_fee_tax = trade_fee * fee_discount + trade_tax
    self.buy_fee = trade_fee * fee_discount


  def calculate(self, buy:Decimal, sell:Decimal, odd_quantity:int):
    cost = sell * self.sell_fee_tax + buy * self.buy_fee
    earn = sell - buy
    return (earn - cost) * odd_quantity


  def can_earn(self, stock_id: str):
    stock = self.monitor.get_stock(stock_id)
    if stock == None: #error handle
      return False

    bidask = stock.get_bid_ask()
    if bidask == None or bidask['entire'] == None or bidask['odd'] == None: #error handle
      return False

    if (stock.available_entire_quantity < 1) or (bidask['entire'].ask_volume[0] < self.safe_entire_quantity):
      return False

    if (bidask['entire'].ask_volume[0]*1000) < (bidask['entire'].ask_volume[0] * self.safe_entire_odd_ratio):
      return False

    return self.calculate(buy = bidask['entire'].ask_price[0], sell = bidask['odd'].ask_price[0], odd_quantity = 1000) >= self.target_benifit



  def action(self, stock_id: str):
    self.log.info('start action: '+stock_id)

    if self.can_earn(stock_id) == False:
      self.log.fatal(stock_id + ' can not earn any more, you have to check the entire processing flow.')
      return False

    # SELL: register sell odd stocks
    stock = self.monitor.get_stock(stock_id)
    # if stock == None: #error handle
    #   return False

    bidask = stock.get_bid_ask()
    # if bidask == None or bidask['entire'] == None or bidask['odd'] == None: #error handle
    #   return False

    sell_odd_price = bidask['odd'].ask_price[0]
    buy_entire_price = bidask['entire'].ask_price[0]

    sell_trade = stock.execute_sell_order(price = sell_odd_price, quantity = self.trade_odd_quantity, is_odd = True)
    while sell_trade.order.id not in self.monitor.trade_list:
      self.log.verbose('wait for register sell trade: '+str(sell_trade.order.id))
      time.sleep(0.001)

    # SELL: wait for the order dealed
    timestamp = time.time()
    while self.monitor.trade_list[sell_trade.order.id].status.status != sj.constant.Status.Filled:
      if (not self.can_earn(stock_id)) or (bidask['odd'].ask_price[0] != sell_odd_price) or (bidask['entire'].ask_price[0] != buy_entire_price):
        self.log.warning('detect the new case, cancel the submitted sell order')
        cancel_trade = stock.cancel_order(sell_trade)
        self.log.verbose(cancel_trade)
        return False
      # print the message peroidly
      time.sleep(0.001)
      if (time.time() - timestamp) >= 2:
        self.log.info('wait for ' + str(sell_trade.order) + ' deal')
        timestamp = time.time()

    # BUY: register buy entire stocks
    stock = self.monitor.get_stock(stock_id)
    buy_trade = stock.execute_buy_order(price = buy_entire_price, quantity = self.trade_entire_quantity, is_odd = False)
    while buy_trade.order.id not in self.monitor.trade_list:
      self.log.verbose('wait for register buy trade: '+str(sell_trade.order.id))
      time.sleep(0.001)

    # BUY: wait for the full dealed
    timestamp = time.time()
    while self.monitor.trade_list[buy_trade.order.id].status.status != sj.constant.Status.Filled:
      time.sleep(0.001)
      if (time.time() - timestamp) >= 10:
        self.log.fatal('over 10 seconds do not deal the buy order, please check the trade status!')
        timestamp = time.time()

    # FINAL deal message
    self.log.info('the full trascation is complete')
    self.monitor.stock_list[stock_id].available_entire_quantity = \
      round(self.monitor.stock_list[stock_id].available_entire_quantity - (self.trade_odd_quantity * 0.001), 3)
    self.log.info('stock ' + str(stock_id) + ' remaining quantity = ' + str(self.monitor.stock_list[stock_id].available_entire_quantity))
    return True

  def get_can_earn_id(self) -> str:
    for stock_id in self.monitor.stock_list:
      if self.can_earn(stock_id):
        self.log.info('get can earn stock ' + stock_id)
        return stock_id
    return None
           

