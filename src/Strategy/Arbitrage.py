# python STL
from decimal import *
import time
import threading

# pip installed
import shioaji as sj
from shioaji import BidAskSTKv1, Exchange

# local
from src.Utils.Logger import Logger
from src.Core.Register import *

class Arbitrage:
  def __init__(self, monitor, trade_fee: Decimal= Decimal(0.001425), trade_tax: Decimal = Decimal(0.003), \
                     fee_discount: Decimal = Decimal(0.4), target_benifit: float = 0):

    # static setting value
    self.safe_odd_quantity = 10000 # detect the interday-odd trading tempture
    self.safe_entire_quantity = 100
    self.trade_entire_quantity = 1
    self.trade_odd_quantity = 999
    self.sell_odd_price = 0
    self.target_benifit = target_benifit
    self.sell_fee_tax = trade_fee * fee_discount + trade_tax
    self.buy_fee = trade_fee * fee_discount

    # class object
    self.log = Logger(self.__class__.__name__)
    self.monitor = monitor
    self.transcation_mutex = dict()


  def calculate(self, buy:Decimal, sell:Decimal, odd_quantity:int):
    cost = sell * self.sell_fee_tax + buy * self.buy_fee
    earn = sell - buy
    return (earn - cost) * odd_quantity


  def can_earn(self, stock_id: str):

    self.sell_odd_price = 0
    stock = self.monitor.get_stock(stock_id)
    if stock == None: #error handle
      return False

    bidask = stock.get_bid_ask()
    if bidask == None or bidask['entire'] == None or bidask['odd'] == None: #error handle
      return False

    if stock.available_entire_quantity < 1:
      return False

    if bidask['entire'].ask_volume[0] < self.safe_entire_quantity or bidask['odd'].bid_volume[0] < self.safe_odd_quantity:
      return False

    # odd.bid_price <= selling price <= odd.ask_price
    self.sell_odd_price = bidask['odd'].bid_price[0]
    while self.sell_odd_price <= bidask['odd'].ask_price[0]:
      if self.calculate(buy = bidask['entire'].ask_price[0], sell = self.sell_odd_price, odd_quantity = self.trade_odd_quantity) >= self.target_benifit:
        return True
      self.sell_odd_price = stock.get_above_price(base = self.sell_odd_price)

    self.sell_odd_price = 0
    return False


  def action(self, stock_id: str):
    if stock_id not in self.transcation_mutex:
      self.transcation_mutex[stock_id] = threading.Lock()

    self.transcation_mutex[stock_id].acquire()
    self.log.info('start action: '+stock_id)

    if self.can_earn(stock_id) == False:
      self.log.fatal(stock_id + ' can not earn any more, you have to check the entire processing flow.')
      self.transcation_mutex[stock_id].release()
      return False

    # SELL: register sell odd stocks
    stock = self.monitor.get_stock(stock_id)
    # if stock == None: #error handle
    #   return False

    bidask = stock.get_bid_ask()
    # if bidask == None or bidask['entire'] == None or bidask['odd'] == None: #error handle
    #   return False

    sell_odd_price = self.sell_odd_price
    buy_entire_price = bidask['entire'].ask_price[0]

    sell_trade = stock.execute_sell_order(price = sell_odd_price, quantity = self.trade_odd_quantity, is_odd = True)
    while sell_trade.order.id not in self.monitor.trade_list:
      self.log.verbose('wait for register sell trade: '+str(sell_trade.order.id))
      time.sleep(0.001)

    # SELL: wait for the order dealed
    timestamp = time.time()
    while self.monitor.trade_list[sell_trade.order.id].status.status != sj.constant.Status.Filled:
      if bidask['entire'].ask_price[0] > buy_entire_price or not self.can_earn(stock_id):
        self.log.warning('detect the \'' + stock_id + '\' new case, try to cancel the submitted sell order')
        while stock.cancel_order(sell_trade) == False:
          self.log.info('cancel \'' + stock_id + '\' sell order fail !!!, retry until it success')
          time.sleep(0.001)

        self.log.info('cancel \'' + stock_id + '\' sell order done.')
        self.transcation_mutex[stock_id].release()
        return False

      # print the message peroidly
      time.sleep(0.001)
      if (time.time() - timestamp) >= 2:
        self.log.verbose('wait for ' + str(sell_trade.order) + ' deal')
        timestamp = time.time()

    # BUY: register buy entire stocks
    stock = self.monitor.get_stock(stock_id)
    buy_entire_price = bidask['entire'].ask_price[0] # retrieve again the lowest buy price.

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

    self.transcation_mutex[stock_id].release()
    return True


  def get_can_earn_id(self) -> str:
    for stock_id in self.monitor.stock_list:
      if (stock_id not in self.transcation_mutex or (stock_id in self.transcation_mutex and not self.transcation_mutex[stock_id].locked())) and \
          self.can_earn(stock_id):
        self.log.info('get can earn stock ' + stock_id)
        return stock_id
    return None
           

