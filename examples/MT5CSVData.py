from datetime import datetime

import backtrader as bt
from backtrader import TimeFrame, date2num


class MT5CSVData(bt.feeds.GenericCSVData):
    params = (
        ('dtformat', '%Y.%m.%d\t%H:%M:%S\t'),  # mind the gap..
        ('datetime', 0),
        # Date Open High Low Close TickVolume Volume Spread
        ('open', 1),
        ('high', 2),
        ('low', 3),
        ('close', 4),
        ('volume', -1),
        ('time', -1),
        ('openinterest', -1),
        # ('timeframe', bt.TimeFrame.Minutes), <--- override them during instantiation
        # ('compression', 60),
    )

