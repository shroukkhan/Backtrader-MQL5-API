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


def download_csv(store: MTraderStore) -> str:
    '''
    Downloads csv data and returns the path..
    '''
    location = '../data'
    frame = bt.TimeFrame.Minutes
    compress = 60
    symbol = 'EURUSD'
    filename = f'{location}/{symbol}-{store.get_granularity(frame=frame, compression=compress)}.csv'
    if not os.path.isfile(filename):
        store.write_csv(
            symbol=symbol,
            timeframe=frame,
            compression=compress,  # M5 = {timeframe}{compression}
            fromdate=datetime.datetime(2021, 10, 1),
            todate=datetime.datetime.now()
        )
    if os.path.isfile(filename):
        return filename
    raise FileNotFoundError(f'CSV not found at {filename}')


def get_data(store, mode: Mode):
    if mode == Mode.STATIC:
        dataname = download_csv(store)
        data = MT5CSVData(
            dataname=dataname,
            nullvalue=0.0,
            dtformat=('%Y.%m.%d %H:%M:%S '),
            fromdate=datetime.datetime(2021, 10, 1),
            datetime=0,
            time=-1,
            open=1,
            high=2,
            low=3,
            close=4,
            volume=5,
            openinterest=-1,
            reverse=False)

        # data = bt.feeds.MT4CSVData(
        #     dataname=dataname)

        return data


if __name__ == '__main__':
    cerebro = bt.Cerebro()

    # mql5 store
    host = '127.0.0.1'  # where is mt5 running?
    store = MTraderStore(host=host, debug=True, datatimeout=10)
    download_csv(store)

    broker = store.getbroker(
        use_positions=True)  # use_positions = get any existing open position from the broker as wel
    cerebro.setbroker(broker)

    data = get_data(store, mode=Mode.STATIC)
    cerebro.adddata(data)

    # cerebro.broker.setcash(100000.00)
    print('Starting portfolio value: %.2f cash: %.2f' % (cerebro.broker.getvalue(), cerebro.broker.getcash()))
    cerebro.run()
    print('Ending portfolio value: %.2f cash: %.2f' % (cerebro.broker.getvalue(), cerebro.broker.getcash()))
