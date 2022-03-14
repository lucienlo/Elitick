# python STL
import threading
import time

# pip installed
import shioaji as sj
from shioaji import BidAskSTKv1, Exchange, Shioaji
from shioaji.order import Trade

# local
from src.Utils.Logger import Logger
from src.Strategy import Arbitrage as arbi

debug = False

class Stock:
  def __init__(self, handle, stock_id: str, available_entire_quantity: float):
    self.log = Logger(self.__class__.__name__)

    self.bidask_mutex = threading.Lock()

    self.handle = handle
    self.id = stock_id
    self.contract = self.handle.Contracts.Stocks[stock_id]
    self.bidask = {'entire': None, 'odd': None}
    self.trade_cb = None

    # available entire quantity
    self.available_entire_quantity = available_entire_quantity


  def set_subscriber(self, trade_cb):
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


  def get_bid_ask(self, key = None):
    ret = None
    self.bidask_mutex.acquire() # mutex protect - start

    if key == 'entire':
      ret = self.bidask['entire']
    elif key == 'odd':
      ret = self.bidask['odd']
    else:
      ret = self.bidask

    self.bidask_mutex.release() # mutex protect - end
    
    return ret
    

  def update_bid_ask(self, bidask: BidAskSTKv1):
    self.bidask_mutex.acquire() # mutex protect - start

    if bidask.intraday_odd == 1:
      self.bidask['odd'] = bidask
    else:
      self.bidask['entire'] = bidask

    self.bidask_mutex.release() # mutex protect - end
    #self.log.verbose(str(bidask))


  def sync_order(self):
    self.handle.update_status(self.handle.stock_account)


  def cancel_order(self, trade):
    sync_order()
    ret = self.handle.cancel_order(trade)
    sync_order()
    return ret.status.status == sj.constant.Status.Cancelled


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
  def __init__(self, handle: Shioaji):
    self.log = Logger(self.__class__.__name__)

    self.is_alive = True

    self.handle = handle
    self.stock_list = dict()
    self.trade_list = dict()
    self.__t_watchdog = None

  def __del__(self):
    self.is_alive = False

  def __cb_bid_ask_manager(self, exchange: Exchange, bidask: BidAskSTKv1):
    ### TO-DO: Here shall only update the information, do not do so many operations.
    #          If it needs, create another handle thread to do.
    self.stock_list[bidask.code].update_bid_ask(bidask)
    self.log.record(bidask)
  
  def cb_trade_manager(self, trade: Trade):
    self.trade_list[trade.order.id] = trade


  def __thread_trade_watchdog(self):
    timestamp = time.time()
    while self.is_alive:
      try:
        self.handle.update_status(self.handle.stock_account)
      except:
        self.log.error('oops! can not successfully get the remote updated status.')
      tlist = self.handle.list_trades()
 
      for trade in tlist:
        self.trade_list[trade.order.id] = trade

      time.sleep(0.1)
      if (time.time() - timestamp) >= 10:
        self.log.verbose('Monitor watchdog is still working')
        timestamp = time.time()

  def add_subscriber(self, stock: Stock, trade_cb):
    self.stock_list[stock.id] = stock
    self.stock_list[stock.id].set_subscriber(trade_cb)

  def get_stock(self, stock_id: str):
    if stock_id not in self.stock_list:
      return None
    return self.stock_list[stock_id]

  def start(self):
    self.handle.quote.set_on_bidask_stk_v1_callback(self.__cb_bid_ask_manager)
    self.__t_watchdog = threading.Thread(target = self.__thread_trade_watchdog, args=())
    self.__t_watchdog.start()
    # self.handle.set_order_callback(__trade_callback_manager)
    


