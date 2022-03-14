import time
import threading, time

from src.Utils.Logger import Logger
from src.Core import Register
from src.Strategy import Arbitrage

class Performer:
  def __init__(self, monitor: Register.Monitor, strategy):
    self.log = Logger(self.__class__.__name__)

    self.is_alive = True
    self.__t_executor = None

    self.monitor = monitor
    self.strategy = strategy

  def __del__(self):
    self.is_alive = False

  def __thread_action_watchdog(self):
    timestamp = time.time()

    while self.is_alive:
      stock_id = self.strategy.get_can_earn_id()
      if stock_id != None:
        self.strategy.action(stock_id)
      else:
        time.sleep(0.001)
      
      if (time.time() - timestamp) >= 10:
        self.log.verbose('Performer watchdog is still working')
        timestamp = time.time()


  def start(self):
    self.__t_executor = threading.Thread(target = self.__thread_action_watchdog, args=())
    self.__t_executor.start()
