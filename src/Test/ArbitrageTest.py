from src.Strategy.Arbitrage import Arbitrage
from src.Core.Register import *
from src.Test.Mock.Struct import *
from src.Core.Auth import *

class ArbitrageTest:
  def __init__(self):
    self.handle = Account().login() #test on the real login

  def test_all(self):
    self.test_can_earn()
    self.test_action()

  def test_can_earn(self):
    component = Arbitrage(MockMonitor(self.handle))
    assert component.can_earn('0000') == False
    assert component.can_earn('2330') == True

  def test_action(self):
    component = Arbitrage(MockMonitor(self.handle))
    component.action('2330')
    component.action('2330')
    component.action('2330')

