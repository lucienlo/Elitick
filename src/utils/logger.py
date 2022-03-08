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

