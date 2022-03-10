import shioaji as sj

import json

from src.Utils import Logger as log

def login():
  try:
    file = open('./secret.json')
    secret = json.load(file)
    file.close()

    log.info(str('login ' + str(secret['acc'])))

    handle = sj.Shioaji()
    result = handle.login(
      person_id = secret['acc'], 
      passwd = secret['pwd'], 
      contracts_cb = lambda security_type: log.info(f"{repr(security_type)} fetch done.")
    )
    if result == False:
      log.fatal('login fail')
      return None

    log.info('load ca')
    result = handle.activate_ca(
      ca_path = secret['ca'],
      ca_passwd = secret['ca_pwd'],
      person_id = secret['ca_pid'],
    )

    if result == False:
      log.fatal('ca fail')
      return None

    return handle

  except IOError:
    log.error('can not find the \'secret.json\'')
    return None

  else:
    with secret:
      print(secret.readlines())
    return None
     

def logout(handle):
  handle.handle()
