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
from src.Test import ut_bidask

account = Account()
log = None
filter_out = ['3227', '00673R']

def main():
  global account
  handle = account.login()
  is_mock = True

  monitor = Monitor(handle = handle, is_mock = is_mock)
  executor = Performer(monitor, Arbitrage(monitor))
  
  for balance in account.get_stock_balances():
    if balance.code in filter_out:
      log.warning('Pass stock_id: ' + str(balance.code)+ ',\t quantity: '+ str(balance.quantity) + '\t')
      continue
    cur_stock = Stock(handle = handle, stock_id = balance.code, available_entire_quantity = balance.yd_quantity, is_mock = is_mock)
    monitor.add_subscriber(cur_stock, monitor.cb_trade_manager)
    log.info('Add stock_id: ' + str(balance.code)+ ',\t quantity: '+ str(balance.quantity) + '\tto monitor')

  monitor.start()
  executor.start()
  
  log.info("all setting done, it's listening.")
  threading.Event().wait()
  log.info("exit ok")


def main_listen_only():
  global account
  handle = account.login()
  is_mock = True

  monitor = Monitor(handle = handle, is_mock = is_mock)
  # executor = Performer(monitor, Arbitrage(monitor))
  
  for balance in account.get_stock_balances():
    cur_stock = Stock(handle = handle, stock_id = balance.code, available_entire_quantity = balance.yd_quantity, is_mock = is_mock)
    monitor.add_subscriber(cur_stock, monitor.cb_trade_manager)
    log.info('Add stock_id: ' + str(balance.code)+ ',\t quantity: '+ str(balance.quantity) + '\tto monitor')

  monitor.start()
  # executor.start()
  
  log.info("all setting done, it's listening.")
  threading.Event().wait()
  log.info("exit ok")


def mock_ut():
  log.fatal('not yet implement UT')
  threading.Event().wait()
  log.info("exit ok")

if __name__ == "__main__":
  log = Logger('Main')
  # main()
  main_listen_only()
  # mock_ut()
  

