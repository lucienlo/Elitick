# python STL
import threading
import time

# pip installed
import shioaji as sj
from shioaji import BidAskSTKv1, Exchange, Shioaji
from shioaji.order import Trade

# local
from src.Utils import Logger as log
from src.Strategy import Arbitrage as arbi

debug = False

class Stock:
  def __init__(self, handle, stock_id: str, is_mock: bool = False):
    self.is_mock = is_mock

    self.handle = handle
    self.id = stock_id
    self.contract = self.handle.Contracts.Stocks[stock_id]
    self.bidask = None
    self.trade_cb = None


  def set_subscriber(self, trade_cb):
    print('ccccccs')
    self.trade_cb = trade_cb

    # listen for complete stock (1000 units)
    self.handle.quote.subscribe(
      self.contract, 
      quote_type = sj.constant.QuoteType.BidAsk,
      version = sj.constant.QuoteVersion.v1,
      intraday_odd = True
    )

    # listen for odd stock (1 unit)
    self.handle.quote.subscribe(
      self.contract,
      quote_type = sj.constant.QuoteType.BidAsk,
      version = sj.constant.QuoteVersion.v1,
      intraday_odd = False
    )


  def update(self, bidask: BidAskSTKv1):
    self.bidask = bidask
    log.verbose(bidask)


  def sync_order(self):
    self.handle.update_status(self.handle.stock_account)


  def cancel_order(self, order_handle):
    sync_order()
    ret = self.handle.cancel_order(order_handle)
    ret.status.status == sj.constant.Status.Cancelled
    sync_order()


  def execute_buy_order(self, price: float, quantity: int, is_odd: bool) -> Trade:
    trade = None

    order = self.handle.Order(
      price = price, 
      quantity = quantity, 
      action = sj.constant.Action.Buy, 
      price_type = sj.constant.StockPriceType.LMT, 
      order_type = sj.constant.TFTOrderType.ROD, 
      order_lot = sj.constant.TFTStockOrderLot.IntradayOdd if is_odd else sj.constant.TFTStockOrderLot.Common, 
      account = self.handle.stock_account,
      timeout = 0,
      cb = self.trade_cb
    )

    trade = self.handle.place_order(self.contract, order)
    return trade


  def execute_sell_order(self, price: float, quantity: int, is_odd: bool) -> Trade:
    trade = None
    order = self.handle.Order(
      price = price, 
      quantity = quantity, 
      action = sj.constant.Action.Sell, 
      price_type = sj.constant.StockPriceType.LMT, 
      order_type = sj.constant.TFTOrderType.ROD, 
      order_lot = sj.constant.TFTStockOrderLot.IntradayOdd if is_odd else sj.constant.TFTStockOrderLot.Common, 
      account = self.handle.stock_account,
      timeout = 0,
      cb = self.trade_cb
    )

    trade = self.handle.place_order(self.contract, order)
    return trade


class Monitor:
  def __init__(self, handle: Shioaji, is_mock: bool = False):
    self.handle = handle
    self.listenee_list = dict()
    self.trade_list = dict()
    self.is_alive = True
    self.__t_watchdog = None

  def __cb_bid_ask_manager(self, exchange: Exchange, bidask: BidAskSTKv1):
    ### TO-DO: Here shall only update the information, do not do so many operations.
    #          If it needs, create another handle thread to do.
    self.listenee_list[bidask.code].update(bidask)

  # def __trade_callback_manager(status, msg):
  #   log.verbose('status# ' + str(status) + ', msg# ' + str(msg))
  #   log.fatal('need to implement __trade_callback_manager api')
  
  def cb_trade_manager(self, trade: Trade):
    self.trade_list[trade.order.id] = trade


  def __thread_trade_watchdog():
    timer = 100
    while self.is_alive:
      self.handle.update_status(self.handle.stock_account)
      tlist = self.handle.list_trades()
 
      for trade in tlist:
        self.trade_list[trade.order.id] = trade

      time.sleep(0.1)
      timer = timer -1
      if timer == 0:
        log.verbose('trade watchdog is still working')
        timer = 100

  def add_subscriber(self, stock: Stock, trade_cb):
    self.listenee_list[stock.id] = stock
    self.listenee_list[stock.id].set_subscriber(trade_cb)

  def get_subscriber(self, stock_id: str):
    return listenee_list[stock_id]

  def start():
    self.handle.quote.set_on_bidask_stk_v1_callback(__cb_bid_ask_manager)
    self.__t_watchdog = threading.Thread(target = __thread_trade_watchdog, args=())
    self.__t_watchdog.start()
    # self.handle.set_order_callback(__trade_callback_manager)
    


