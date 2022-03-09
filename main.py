import json
import os, threading
from decimal import *

import shioaji as sj
# import pandas as pd
from shioaji import BidAskSTKv1, Exchange

from src.connection import auth, register
from src.utils import logger as log
from src.strategy import arbitrage as arbi
from src.test import ut_bidask


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
  register.start_watch_bid_ask(handle = None, isMock = True)

  #simulate the data update
  register.quote_callback(None, ut_bidask.get_mock_object(isOdd = True))
  register.quote_callback(None, ut_bidask.get_mock_object(isOdd = False))

if __name__ == "__main__":
   main()
  #mock_ut()
