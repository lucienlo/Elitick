# import json
import signal, sys
import os, threading, time
from decimal import *

import shioaji as sj
from shioaji import BidAskSTKv1, Exchange

from src.Core.Performer import Performer
from src.Core.Auth import Account
from src.Core.Register import *
from src.Utils.Logger import Logger
from src.Strategy.Arbitrage import *


from src.Test.ArbitrageTest import *

account = Account()
log = None
filter_out = ['00673R']
# filter_out = []

def main():
  log = Logger('Main')
  global account
  handle = account.login()

  monitor = Monitor(handle = handle)
  executor = Performer(monitor, Arbitrage(monitor))
  
  for balance in account.get_stock_balances():
    if balance.code in filter_out:
      log.warning('Pass stock_id: ' + str(balance.code)+ ',\t quantity: '+ str(balance.quantity) + '\t')
      continue
    cur_stock = Stock(handle = handle, stock_id = balance.code, available_entire_quantity = balance.yd_quantity)
    monitor.add_subscriber(cur_stock, monitor.cb_trade_manager)
    log.info('Add stock_id: ' + str(balance.code)+ ',\t quantity: '+ str(balance.quantity) + '\tto monitor')

  monitor.start()
  executor.start()
  
  log.info("all setting done, it's listening.")
  threading.Event().wait()
  log.info("exit ok")


def main_listen_only():
  log = Logger('Main')
  global account
  handle = account.login()

  # monitor = Monitor(handle = handle)
  monitor = Monitor(handle = handle, refresh_sec = 0.25)
  # executor = Performer(monitor, Arbitrage(monitor))
  
  for balance in account.get_stock_balances():
    cur_stock = Stock(handle = handle, stock_id = balance.code, available_entire_quantity = balance.yd_quantity)
    monitor.add_subscriber(cur_stock, monitor.cb_trade_manager)
    log.info('Add stock_id: ' + str(balance.code)+ ',\t quantity: '+ str(balance.quantity) + '\tto monitor')

  monitor.start()
  # executor.start()
  
  log.info("all setting done, it's listening.")
  threading.Event().wait()
  log.info("exit ok")


def mock_ut():
  ArbitrageTest().test_all()
  # log.info("exit ok")

if __name__ == "__main__":
  main()
  # main_listen_only()
  # mock_ut()
  

