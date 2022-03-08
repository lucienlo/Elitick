import shioaji as sj

import json

from src.utils import logger as log

def login():
  try:
    file = open('./secret.json')
    secret = json.load(file)
    file.close()

    log.info(str('login ' + str(secret['acc'])))

    handle = sj.Shioaji()
    handle.login(
      person_id = secret['acc'], 
      passwd = secret['pwd'], 
      contracts_cb = lambda security_type: log.info(f"{repr(security_type)} fetch done.")
    )

    # handle.activate_ca(
    #   ca_path = secret['ca'],
    #   ca_passwd = secret['ca_pwd'],
    #   person_id = secret['ca_pid'],
    # )

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