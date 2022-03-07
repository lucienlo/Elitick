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

    return handle

  except IOError:
    log.error('can not find the \'secret.json\'')

  else:
    with secret:
      print(secret.readlines())
     

def logout(handle):
  handle.handle()
