from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime, timedelta  # For datetime objects

import backtrader as bt

from backtradermql5 import MTraderStore

# Import the backtrader platform

if __name__ == '__main__':
    # connect to metatrader
    host = '127.0.0.1'
    data_folder = 'C:\\Users\\skhan\\AppData\\Roaming\\MetaQuotes\\Terminal\\D0E8209F77C8CF37AD8BF550E51FF075\\MQL5\\Files\\Data\\'
    symbol = 'EURUSD'
    timeframe = 'M1'
    store = MTraderStore(host=host, debug=False, datatimeout=100)

    store.reset_server()
    start_date = datetime.now() - timedelta(minutes=500)

    # filepath = f'{data_folder}{symbol}-{timeframe}.csv'
    # if not exists(filepath):
    #     store.write_csv(symbol='EURUSD',
    #                     fromdate=start_date,
    #                     timeframe=bt.TimeFrame.Minutes
    #                     )

    data = store.getdata(dataname=symbol, timeframe=bt.TimeFrame.Ticks, fromdate=start_date)

    cerebro = bt.Cerebro()
    broker = store.getbroker(use_positions=True)
    cerebro.setbroker(broker)

    start_date = datetime.now() - timedelta(minutes=500)

    cerebro.resampledata(data,
                         timeframe=bt.TimeFrame.Seconds,
                         compression=30
                         )
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getcash())
    cerebro.run(stdstats=False)
    cerebro.plot(style='candlestick', volume=False)
