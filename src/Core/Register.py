# python STL
import threading
import time

# pip installed
import shioaji as sj
from shioaji import BidAskSTKv1, TickSTKv1, Exchange, Shioaji
from shioaji.order import Trade

# local
from src.Utils.Logger import Logger
from src.Strategy import Arbitrage as arbi

debug = False

class Stock:
  def __init__(self, handle, stock_id: str, available_entire_quantity: float):
    self.log = Logger(self.__class__.__name__)

    self.bidask_mutex = threading.Lock()
    self.tick_mutex = threading.Lock()

    self.handle = handle
    self.id = stock_id
    self.contract = self.handle.Contracts.Stocks[stock_id]
    self.bidask = {'entire': None, 'odd': None}
    self.tick = {'entire': None, 'odd': None}
    self.trade_cb = None

    # available entire quantity
    self.available_entire_quantity = available_entire_quantity


  def set_subscriber(self, trade_cb):
    self.trade_cb = trade_cb

    # listen bid&ask for complete stock (1000 units)
    self.handle.quote.subscribe(
      self.contract, 
      quote_type = sj.constant.QuoteType.BidAsk,
      version = sj.constant.QuoteVersion.v1,
      intraday_odd = True
    )

    # listen bid&ask for odd stock (1 unit)
    self.handle.quote.subscribe(
      self.contract,
      quote_type = sj.constant.QuoteType.BidAsk,
      version = sj.constant.QuoteVersion.v1,
      intraday_odd = False
    )

    # listen tick for complete stock (1000 units)
    self.handle.quote.subscribe(
      self.contract,
      quote_type = sj.constant.QuoteType.Tick,
      version = sj.constant.QuoteVersion.v1,
      intraday_odd = True
    )

    # listen tick for odd stock (1 unit)
    self.handle.quote.subscribe(
      self.contract,
      quote_type = sj.constant.QuoteType.Tick,
      version = sj.constant.QuoteVersion.v1,
      intraday_odd = False
    )


  def get_bid_ask(self, key: str = None) -> BidAskSTKv1:
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


  def get_tick(self, key: str = None) -> TickSTKv1:
    ret = None
    self.tick_mutex.acquire() # mutex protect - start

    if key == 'entire':
      ret = self.tick['entire']
    elif key == 'odd':
      ret = self.tick['odd']
    else:
      ret = self.tick

    self.tick_mutex.release() # mutex protect - end
    
    return ret


  def update_tick(self, tick:TickSTKv1):
    self.tick_mutex.acquire() # mutex protect - start

    if tick.intraday_odd == 1:
      self.tick['odd'] = tick
    else:
      self.tick['entire'] = tick

    self.tick_mutex.release() # mutex protect - end
    #self.log.verbose(str(tick))


  def sync_order(self):
    try:
      self.handle.update_status(self.handle.stock_account)
    except:
      self.log.error('oops! can not successfully get the remote updated status.')
      return False
    return True


  def cancel_order(self, trade: Trade):
    while self.sync_order() == False:
      time.sleep(0.001)
      self.log.warning('cancel_order try to sync order again (before cancel).')

    ret = self.handle.cancel_order(trade)

    while self.sync_order() == False:
      time.sleep(0.001)
      self.log.warning('cancel_order try to sync order again (after cancel).')

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


  def get_above_price(self, base: float) -> float:
    if 0.01 <= base and base < 10:
      return round(base + 0.01, 2)

    elif 10 <= base and base < 50:
      return round(base + 0.05, 2)

    elif 50 <= base and base < 100:
      return round(base + 0.1, 1)

    elif 100 <= base and base < 500:
      return round(base + 0.5, 1)

    elif 500 <= base and base < 1000:
      return round(base + 1, 0)

    elif 1000 <= base:
      return round(base + 5, 0)

    return -1


  def get_below_price(self, base: float) -> float:
    if 0.01 < base and base <= 10:
      return round(base - 0.01, 2)

    elif 10 < base and base <= 50:
      return round(base - 0.05, 2)

    elif 50 < base and base <= 100:
      return round(base - 0.1, 1)

    elif 100 < base and base <= 500:
      return round(base - 0.5, 1)

    elif 500 < base and base <= 1000:
      return round(base - 1, 0)

    elif 1000 < base:
      return round(base - 5, 0)

    return -1


class Monitor:
  def __init__(self, handle: Shioaji, refresh_sec: float = 0.05):
    self.log = Logger(self.__class__.__name__)
    self.refresh_sec = refresh_sec
    self.is_alive = True

    self.handle = handle
    self.stock_list = dict()
    self.trade_list = dict()
    self.__t_watchdog = None


  def __del__(self):
    self.is_alive = False
    if self.__t_watchdog != None:
      self.__t_watchdog.join()


  def _cb_bid_ask_manager(self, exchange: Exchange, bidask: BidAskSTKv1):
    self.stock_list[bidask.code].update_bid_ask(bidask)
    self.log.record(bidask)


  def _cb_tick_manager(self, exchange: Exchange, tick:TickSTKv1):
    self.stock_list[tick.code].update_tick(tick)
    self.log.record(tick)

  
  def cb_trade_manager(self, trade: Trade):
    self.trade_list[trade.order.id] = trade
    self.log.record(trade)


  def __thread_trade_watchdog(self):
    timestamp = time.time()
    while self.is_alive:
      try:
        self.handle.update_status(self.handle.stock_account)
      except:
        self.log.error('oops! can not successfully get the remote updated status.')
      tlist = self.handle.list_trades()
 
      for trade in tlist:
        if trade.order.id not in self.trade_list or \
            self.trade_list[trade.order.id].status.status != trade.status.status:
          self.log.record(trade)
        self.trade_list[trade.order.id] = trade

      time.sleep(self.refresh_sec)
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
    self.handle.quote.set_on_bidask_stk_v1_callback(self._cb_bid_ask_manager)
    self.handle.quote.set_on_tick_stk_v1_callback(self._cb_tick_manager)
    self.__t_watchdog = threading.Thread(target = self.__thread_trade_watchdog, args=())
    self.__t_watchdog.start()
    # self.handle.set_order_callback(__trade_callback_manager)
    


