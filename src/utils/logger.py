#python STL
import pickle

def show(type, msg):
  print('>> ['+type+']\t: '+ msg)

def info(msg):
  show('info', msg)

def warning(msg):
  show('warning', msg)

def error(msg):
  show('error', msg)

def fatal(msg):
  show('fatal', msg)

def toObj(obj):
  with open('bid_and_ask_history.pkl', 'ab+') as f:
    pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
  

