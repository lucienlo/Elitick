class LogInstance:
  def __new__(self, create_timestamp: str):
    if not hasattr(self, 'instance'):
      self.instance = super(LogInstance, self).__new__(self)
      self.log_file = open(create_timestamp+'_history.log', 'a+', buffering=1)
      self.pkl_file = open(create_timestamp+'_record.pkl', 'ab+', buffering=1)
    return self.instance