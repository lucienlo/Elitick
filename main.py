import json
import os, threading
from decimal import *

import shioaji as sj
# import pandas as pd
from shioaji import BidAskSTKv1, Exchange

from src.Connection import Auth, Register
from src.Utils import Logger as log
from src.Strategy import Arbitrage as arbi
from src.Test import ut_bidask


def main():
  handle = auth.login()
  if handle == None:
    return False;

  register.bid_ask_entire_and_odd(handle, "2330")
  register.start_watch_bid_ask(handle)

  log.info("all setting done, it's listening...")
  threading.Event().wait()

  logout(handle)
  return True


def mock_ut():
  handle = Auth.login()
  is_mock = True

  monitor = Register.Monitor(handle = handle, is_mock = is_mock)
  tse2330 = Register.Stock(handle = handle, stock_id = '2330', is_mock = is_mock)
  tse3227 = Register.Stock(handle = handle, stock_id = '3327', is_mock = is_mock)
  monitor.add_subscriber(tse2330, monitor.cb_trade_manager)
  monitor.add_subscriber(tse3227, monitor.cb_trade_manager)

  monitor.start()

  log.info("all setting done, it's listening...")
  threading.Event().wait()
  logout(handle)


if __name__ == "__main__":
  #main()
  mock_ut()
