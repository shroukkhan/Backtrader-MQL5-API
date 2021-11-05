from datetime import datetime, timedelta

import backtrader as bt

from backtradermql5.mt5store import MTraderStore


class SmaCross(bt.SignalStrategy):

    def __init__(self):
        self.buy_order = None
        self.live_data = False

    def next(self):
        if self.buy_order is None:
            self.buy_order = self.buy_bracket(limitprice=1.13, stopprice=1.10, size=0.1, exectype=bt.Order.Market)

        if self.live_data:
            cash = self.broker.getcash()

            # Cancel order
            if self.buy_order is not None:
                self.cancel(self.buy_order[0])

        else:
            # Avoid checking the balance during a backfill. Otherwise, it will
            # Slow things down.
            cash = 'NA'

        for data in self.datas:
            print(
                f'{data.datetime.datetime()} - {data._name} | Cash {cash} | O: {data.open[0]} H: {data.high[0]} L: {data.low[0]} C: {data.close[0]} V:{data.volume[0]}')

    def notify_data(self, data, status, *args, **kwargs):
        dn = data._name
        dt = datetime.now()
        msg = f'Data Status: {data._getstatusname(status)}'
        print(dt, dn, msg)
        if data._getstatusname(status) == 'LIVE':
            self.live_data = True
        else:
            self.live_data = False


cerebro = bt.Cerebro()
cerebro.addstrategy(SmaCross)

store = MTraderStore()

# comment next 2 lines to use backbroker for backtesting with MTraderStore
broker = store.getbroker(use_positions=True)
cerebro.setbroker(broker)

start_date = datetime.now() - timedelta(minutes=500)

data = store.getdata(dataname='EURUSD', timeframe=bt.TimeFrame.Ticks,
                     fromdate=start_date)  # , useask=True, historical=True)
# the parameter "useask" will request the ask price insetad if the default bid price

cerebro.resampledata(data,
                     timeframe=bt.TimeFrame.Seconds,
                     compression=30
                     )

cerebro.run(stdstats=False)
cerebro.plot(style='candlestick', volume=False)
