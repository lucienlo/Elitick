#python STL
import pickle
import threading
from src.Utils.LogInstance import *
from datetime import datetime, timezone, timedelta

tz = timezone(timedelta(hours=+8))

debug = True

class Logger:
  def __show(self, type:str, msg: str):
    formatted = str(datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")) + '  ' + type + \
                ' ' + str(self.tid).ljust(5) + ' ' +self.label.ljust(15) + ' : ' + msg
    self.file.log_file.write(formatted+'\n')
    print(formatted)


  def __init__(self, label: str):
    self.file = LogInstance(str(datetime.now(tz).strftime("%Y%m%d%H%M%S")))
    self.label = label
    self.tid = 0

    try:
      self.tid = threading.local().threadid
    except AttributeError:
      import ctypes
      libc = ctypes.cdll.LoadLibrary('libc.so.6')
      SYS_gettid = 186
      self.tid = threading.local().threadid = libc.syscall(SYS_gettid)


  def __del__(self):
    if not self.file.log_file.closed:
      self.file.log_file.flush()

    if not self.file.pkl_file.closed:
      self.file.pkl_file.flush()


  def verbose(self, msg: str):
    if debug:
      self.__show('V', msg)


  def info(self, msg: str):
    self.__show('I', msg)


  def warning(self, msg: str):
    self.__show('W', msg)


  def error(self, msg: str):
    self.__show('E', msg)


  def fatal(self, msg: str):
    self.__show('F', msg)


  def record(self, obj):
    pickle.dump(obj, self.file.pkl_file, pickle.HIGHEST_PROTOCOL)


  def load_pkl(self, path):
    data = []
    with open(path, 'rb') as f:
      while True:
        try:
          data.append(pickle.load(f))
        except EOFError:
          return data
    return data

  

