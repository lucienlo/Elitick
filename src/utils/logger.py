#python STL
import pickle

debug = True

def __show(type, msg):
  print('>> ['+type+']\t: '+ msg)

def verbose(msg):
  if debug:
  	__show('verbose', msg)

def info(msg):
  __show('info', msg)

def warning(msg):
  __show('warning', msg)

def error(msg):
  __show('error', msg)

def fatal(msg):
  __show('fatal', msg)


def toObj(obj):
  with open('bid_and_ask_history.pkl', 'ab+') as f:
    pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
  

