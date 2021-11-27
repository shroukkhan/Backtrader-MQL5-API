from __future__ import (absolute_import, division, print_function, unicode_literals)

import datetime
import os
from enum import Enum

import backtrader as bt

from backtradermql5.mt5store import MTraderStore
from examples.MT5CSVData import MT5CSVData


class Mode(Enum):
    LIVE = 1,
    STATIC = 2


class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        '''Logging utility function'''
        dt: datetime = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # keep a reference to close line in data[0] dataseries
        self.dataclose = self.datas[0].close

    def next(self):
        # Simply log the closeing price of the series
        self.log('Close, %.5f' % self.dataclose[0])

        if self.dataclose[0] < self.dataclose[-1] < self.dataclose[-2]:
            self.log('BUY CREATE, %.5f' % self.dataclose[0])
            self.buy()


def download_csv(store: MTraderStore, timeframe: str, compression: int) -> str:
    '''
    Downloads csv data and returns the path..
    '''
    location = '../data'
    symbol = 'EURUSD'
    filename = f'{location}/{symbol}-{store.get_granularity(frame=timeframe, compression=compression)}.csv'
    if not os.path.isfile(filename):
        store.write_csv(
            symbol=symbol,
            timeframe=timeframe,
            compression=compression,  # M5 = {timeframe}{compression}
            fromdate=datetime.datetime(2021, 10, 1),
            todate=datetime.datetime.now()
        )
    if os.path.isfile(filename):
        return filename
    raise FileNotFoundError(f'CSV not found at {filename}')


def get_data(store, mode: Mode):
    if mode == Mode.STATIC:
        timeframe = bt.TimeFrame.Minutes
        compression = 60
        dataname = download_csv(store, timeframe, compression)
        data = MT5CSVData(dataname=dataname,
                          timeframe=timeframe,
                          compression=compression)

        return data


if __name__ == '__main__':
    cerebro = bt.Cerebro()

    # mql5 store
    host = '127.0.0.1'  # where is mt5 running?
    store = MTraderStore(host=host, debug=True, datatimeout=10)

    broker = store.getbroker(
        use_positions=True)  # use_positions = get any existing open position from the broker as wel
    cerebro.setbroker(broker)

    data = get_data(store, mode=Mode.STATIC)
    cerebro.adddata(data)  # insert order 0

    cerebro.addstrategy(TestStrategy)  # add order 0 :P

    # cerebro.broker.setcash(100000.00)
    print('Starting portfolio value: %.5f cash: %.5f' % (cerebro.broker.getvalue(), cerebro.broker.getcash()))
    cerebro.run()
    print('Ending portfolio value: %.5f cash: %.5f' % (cerebro.broker.getvalue(), cerebro.broker.getcash()))
