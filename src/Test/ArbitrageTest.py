import threading

from src.Strategy.Arbitrage import Arbitrage
from src.Core.Register import *
from src.Test.Mock.Struct import *
from src.Core.Auth import *

class ArbitrageTest:
  def __init__(self):
    self.handle = Account().login() #test on the real login
    self.mointor = MockMonitor(self.handle)

  def test_all(self):
    # self.test_can_earn()
    # self.test_action()
    self.test_monitor_simulation()

  def test_can_earn(self):
    component = Arbitrage(self.mointor)
    assert component.can_earn('0000') == False
    assert component.can_earn('2330') == True

  def test_action(self):
    component = Arbitrage(self.mointor)
    stock_id = '2330'
    threading.Thread(target = component.action, args=(stock_id, )).start() 
    component.action('2330')
    component.action('2330')
    component.action('2330')


  def test_monitor_simulation(self):
    self.mointor.start()

