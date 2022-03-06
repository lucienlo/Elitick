import json

import shioaji as sj
import pandas as pd
from shioaji import BidAskSTKv1, Exchange

def login(api, acc, pwd):
  api.login(
    person_id = acc, 
    passwd = pwd, 
    contracts_cb = lambda security_type: print(f"{repr(security_type)} fetch done.")
  )

def logout(api):
  api.logout()

def subscribe_bidAsk(api, isOdd):
  return api.quote.subscribe(
    api.Contracts.Stocks["2330"], 
    quote_type = sj.constant.QuoteType.Tick,
    version = sj.constant.QuoteVersion.v1,
    intraday_odd = isOdd
  )

def quote_callback(exchange: Exchange, bidask:BidAskSTKv1):
    print(f"Exchange: {exchange}, BidAsk: {bidask}")

def main():
  api = sj.Shioaji()
  with open('./secret.json') as file:
    info = json.load(file)

  print('login with: ' + info['acc'])
  login(api, info['acc'], info['pwd'])

  odd_ba = subscribe_bidAsk(api, isOdd=True)
  api.quote.set_on_bidask_stk_v1_callback(quote_callback)
  print(df)

  logout(api)

if __name__ == "__main__":
  main()
