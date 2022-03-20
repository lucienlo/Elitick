
from decimal import *
from shioaji import BidAskSTKv1, Exchange
import shioaji as sj
from shioaji.order import OrderStatus, Trade, Order
from src.Core import Register
from src.Utils.Logger import *
import datetime
import sched
import time

g_trade = Trade(contract = sj.contracts.Stock(
        exchange=sj.constant.Exchange.TSE, 
        code='2330', 
        symbol='TSE2330', 
        name='台積電', 
        category='1', 
        day_trade='Yes'
    ), order = Order(
      id = '2bc5ae85',
      price = 600, 
      quantity = 1000, 
      action = sj.constant.Action.Sell, 
      price_type = sj.constant.StockPriceType.LMT, 
      order_type = sj.constant.TFTOrderType.ROD, 
      order_lot = sj.constant.TFTStockOrderLot.IntradayOdd,
      account = None,
      timeout = 0,
      cb = None
    ), status = OrderStatus(
        id='2bc5ae85', 
        status=sj.constant.Status.Filled, 
        status_code='0', 
        order_datetime=datetime.datetime(2020, 3, 9, 8, 59, 42), 
        deals=[])
    )


class MockStock(Register.Stock):
  def __init__(self, handle, stock_id: str, available_entire_quantity: float):
    self.log = Logger(self.__class__.__name__, debug = False)

    self.bidask_mutex = threading.Lock()

    self.handle = handle
    self.id = stock_id
    self.contract = None
    self.bidask = {'entire': None, 'odd': None}
    self.trade_cb = None

    # available entire quantity
    self.available_entire_quantity = available_entire_quantity

  def cancel_order(self, trade):
    self.log.verbose('cancel_order')
    return True

  def set_subscriber(self, trade_cb):
    self.log.verbose('set_subscriber')

  def get_bid_ask(self, key = None):
    if self.id != '2330':
      return None

    self.bidask = {
      "entire" : BidAskSTKv1(
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
      ),
      "odd" : BidAskSTKv1(
        code = '2330',
        datetime = datetime.datetime(2021, 7, 2, 13, 17, 45, 743299),
        # bid_price = [Decimal('593'), Decimal('592'), Decimal('591'), Decimal('590'), Decimal('589')],
        bid_price = [Decimal('590'), Decimal('592'), Decimal('591'), Decimal('590'), Decimal('589')],  
        bid_volume = [59391, 224490, 74082, 68570, 125246], 
        diff_bid_vol = [49874, 101808, 23863, 38712, 77704], 
        ask_price = [Decimal('594'), Decimal('595'), Decimal('596'), Decimal('597'), Decimal('598')], 
        # ask_price = [Decimal('594'), Decimal('595'), Decimal('596'), Decimal('597'), Decimal('598')],
        ask_volume = [26355, 9680, 18087, 11773, 3568], 
        diff_ask_vol = [13251, -14347, 39249, -20397, -10591], 
        suspend = 0, 
        simtrade = 1, 
        intraday_odd = 1
      )
    }
    return self.bidask

  def update_bid_ask(self, bidask: BidAskSTKv1):
    self.log.verbose('update_bid_ask')

  def sync_order(self):
    self.log.verbose('sync_order')
    return True

  def execute_buy_order(self, price: float, quantity: int, is_odd: bool) -> Trade:
    order = self.handle.Order(
      id = '2bc5ae85',
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
    trade = Trade(contract = g_trade.contract, order = order, status = g_trade.status)
    self.log.verbose(str(trade))

    return trade


  def execute_sell_order(self, price: float, quantity: int, is_odd: bool) -> Trade:
    order = self.handle.Order(
      id = '2bc5ae85',
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
    trade = Trade(contract = g_trade.contract, order = order, status = g_trade.status)
    self.log.verbose(str(trade))

    return g_trade


class MockMonitor(Register.Monitor):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.base_time = None
    self.schedule = sched.scheduler(time.time, time.sleep)
    self.streaming = dict()
    self.__load_simulation_data('/home/work/src/Test/Asset/simulation.pkl')
    self.__set_bid_ask_streaming(obj_type = BidAskSTKv1)


  def __load_simulation_data(self, path):
    self.log.info('load simulation data from \'' + path + '\'')
    data = self.log.load_pkl(path)
    for obj in data:
      obj_type = type(obj)
      if obj_type not in self.streaming:
        self.streaming[obj_type] = list()

      self.streaming[obj_type].append(obj)
    self.log.info('load simulation data done!')


  def __set_bid_ask_streaming(self, obj_type):
    self.log.info('set bid & ask simulation streaming')

    self.base_time = None
    for event in self.streaming[obj_type]:
      if self.base_time == None:
        self.base_time = event.datetime.timestamp()

      if self.get_stock(event.code) == None:
        self.add_subscriber(event.code)

      new_ts = event.datetime.timestamp() - self.base_time
      self.schedule.enter(new_ts, 0, self._cb_bid_ask_manager,(None, event))

    self.log.info('set bid & ask simulation streaming done!')


  def get_stock(self, stock_id: str):
    self.trade_list['2bc5ae85'] = g_trade
    if stock_id not in self.stock_list:
      self.stock_list[stock_id] = MockStock(self.handle, stock_id, 2)
    return self.stock_list[stock_id]


  def start(self):
    super().start()
    self.schedule.run()

  