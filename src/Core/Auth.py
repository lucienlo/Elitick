import shioaji as sj
import json

from src.Utils.Logger import Logger

class Account:
  def __init__(self):
    self.log = Logger(self.__class__.__name__)
    self.handle = sj.Shioaji()

  def login(self):
    try:
      file = open('./secret.json')
      secret = json.load(file)
      file.close()

      self.log.info(str('login ' + str(secret['acc'])))

      result = self.handle.login(
        person_id = secret['acc'], 
        passwd = secret['pwd'], 
        contracts_cb = lambda security_type: self.log.info(f"{repr(security_type)} fetch done.")
      )
      if result == False:
        self.log.fatal('login fail')
        return None

      self.log.info('load CA')
      result = self.handle.activate_ca(
        ca_path = secret['ca'],
        ca_passwd = secret['ca_pwd'],
        person_id = secret['ca_pid'],
      )

      if result == False:
        self.log.fatal('ca fail')
        return None

      return self.handle

    except IOError:
      self.log.error('can not find the \'secret.json\'')
      return None

    else:
      with secret:
        print(secret.readlines())
      return None


  def logout(self):
    self.handle.logout()

  def get_stock_balances(self):
    return self.handle.list_positions(self.handle.stock_account)
