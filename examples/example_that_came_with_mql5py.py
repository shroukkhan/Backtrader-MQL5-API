import pytz
import backtrader as bt
import backtrader.indicators as btind
from backtradermql5.mt5store import MTraderStore
from backtradermql5.mt5indicator import getMTraderIndicator
from backtradermql5.mt5chart import MTraderChart, ChartIndicator
from datetime import datetime, timedelta

# from regressionchannel3 import LinearRegression
# from ohlc import OHLC


class SmaCross(bt.SignalStrategy):
    def __init__(self, store):
        self.buy_order = None
        self.live_data = False

        # Attach and retrieve values from the MT5 indicator "Examples/Custom Moving Average"
        self.mt5cma = getMTraderIndicator(
            # MTraderStorestore instance
            store,
            # Data feed to run the indicator calculations on
            self.datas[0],
            # Set accessor(s) for the indicator output lines
            ("cma",),
            # MT5 inidicator name
            indicator="Examples/Custom Moving Average",
            # Indicator parameters.
            #   Any omitted values will use the defaults as defind by the indicator.
            #   The parameter "params" must exist. If you want to use only the indicator defaults,
            #   pass an empty list: params=[],
            params=[13, 0, "MODE_SMMA"],
        )()

        # Instantiating backtrader indicator Bollinger Bands and Moving Averages
        #   Important: This needs to come before instantiating a chart window
        #   with backtradermql5.mt5indicator.MTraderChart. Otherwise backtrader will fail.
        self.bb = btind.BollingerBands(self.datas[0])
        self.sma = btind.MovingAverageSimple(self.datas[0])

        # -----> Experimental feature BEGIN
        # The feaure to plot data to MT5 chart windows WILL plot false data at this point in time. More work is needed.
        # Plot the backtrader BollingerBand and SMA indicators to a chart window in MT5

        def addChart(chart, bb, sma):
            # Instantiate new indicator and draw to the main window. The parameter idx=0 specifies wether to plot to the
            # main window (idx=0) or a subwindow (idx=1 for the first subwindow, idx=2 for the second etc.).
            indi0 = ChartIndicator(idx=0, shortname="Bollinger Bands")

            # # Add line buffers
            indi0.addline(
                bb.top,
                style={
                    "linelabel": "Top",
                    "color": "clrBlue",
                },
            )
            indi0.addline(
                bb.mid,
                style={
                    "linelabel": "Middle",
                    "color": "clrYellow",
                },
            )
            indi0.addline(
                bb.bot,
                style={
                    "linelabel": "Bottom",
                    "color": "clrGreen",
                },
            )

            # Add the indicator to the chart and draw the line buffers.
            chart.addchartindicator(indi0)

            # # Instantiate second indicator to draw to the first sub-window and add line buffers
            indi1 = ChartIndicator(idx=1, shortname="Simple Moving Average")
            indi1.addline(
                sma.sma,
                style={"linelabel": "SMA", "color": "clrBlue", "linestyle": "STYLE_DASH", "linewidth": 2},
            )
            chart.addchartindicator(indi1)

        # Instantiate a new chart window and plot
        chart = MTraderChart(self.datas[0], realtime=False)
        addChart(chart, self.bb, self.sma)

        # Experimental feature END <-----

    def next(self):
        # Uncomment below to execute trades
        # if self.buy_order is None:
        #     self.buy_order = self.buy_bracket(limitprice=1.13, stopprice=1.10, size=0.1, exectype=bt.Order.Market)

        if self.live_data:
            cash = self.broker.getcash()

            # Cancel order
            if self.buy_order is not None:
                self.cancel(self.buy_order[0])

        else:
            # Avoid checking the balance during a backfill. Otherwise, it will
            # Slow things down.
            cash = "NA"

        for data in self.datas:
            print(
                f"{data.datetime.datetime()} - {data._name} | Cash {cash} | O: {data.open[0]} H: {data.high[0]} L: {data.low[0]} C: {data.close[0]} V:{data.volume[0]}"
            )
        print("")
        print(f"MT5 indicator 'Examples/Custom Moving Average': {self.mt5cma.cma[0]}")

    def notify_data(self, data, status, *args, **kwargs):
        dn = data._name
        dt = datetime.now()
        msg = f"Data Status: {data._getstatusname(status)}"
        print(dt, dn, msg)
        if data._getstatusname(status) == "LIVE":
            self.live_data = True
        else:
            self.live_data = False


# If MetaTrader runs locally
# host = "localhost"
# If Metatrader runs at differnt address
host = "127.0.0.1"

store = MTraderStore(host=host, debug=True, datatimeout=10)

cerebro = bt.Cerebro()

cerebro.addstrategy(SmaCross, store)

broker = store.getbroker(use_positions=True)
cerebro.setbroker(broker)

start_date = datetime.now() - timedelta(hours=60)

data = store.getdata(
    dataname="EURUSD",
    timeframe=bt.TimeFrame.Minutes,
    fromdate=start_date,
    compression=1,
    # tz=pytz.timezone("Europe/Berlin"),
    # useask=True,
    historical=True,
)
cerebro.adddata(data)

cerebro.run(stdstats=False)
