'''
Author: www.backtest-rookies.com

MIT License

Copyright (c) 2020 backtest-rookies.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
import backtrader as bt
from datetime import datetime
import pandas as pd
import numpy as np
from alpha_vantage.timeseries import TimeSeries

# IMPORTANT!
# ----------
# Register for an API at:
# https://www.alphavantage.co/support/#api-key
# Then insert it here.
Apikey = 'KEKRESWE1Q7OVXTJ'


def adjust(date, close, adj_close, in_col, rounding=4):
    '''
    If using forex or Crypto - Change the rounding accordingly!
    '''
    try:
        factor = adj_close / close
        return round(in_col * factor, rounding)
    except ZeroDivisionError:
        print('WARNING: DIRTY DATA >> {} Close: {} | Adj Close {} | in_col: {}'.format(date, close, adj_close, in_col))
        return 0


def alpha_vantage_daily_adjusted(symbol_list, compact=False, debug=False, rounding=4, *args, **kwargs):
    '''
    Helper function to download Alpha Vantage Data.

    My framework expects a nested list to be returned containing the
    pandas dataframe and the name of the feed.
    '''
    data_list = list()

    size = 'compact' if compact else 'full'

    for symbol in symbol_list:

        if debug:
            print('Downloading: {}, Size: {}'.format(symbol, size))

        # Submit our API and create a session
        alpha_ts = TimeSeries(key=Apikey, output_format='pandas')

        # Get the data
        data, meta_data = alpha_ts.get_daily_adjusted(symbol=symbol, outputsize=size)
        # data, meta_data = alpha_ts.get_daily(symbol=symbol, outputsize=size)

        if debug:
            print(data)

        # Convert the index to datetime.
        data.index = pd.to_datetime(data.index)
        # Adjust the rest of the data
        data['adj open'] = np.vectorize(adjust)(data.index.date, data['4. close'], data['5. adjusted close'],
                                                data['1. open'], rounding=rounding)
        data['adj high'] = np.vectorize(adjust)(data.index.date, data['4. close'], data['5. adjusted close'],
                                                data['2. high'], rounding=rounding)
        data['adj low'] = np.vectorize(adjust)(data.index.date, data['4. close'], data['5. adjusted close'],
                                               data['3. low'], rounding=rounding)

        # Extract the colums we want to work with and rename them.
        data = data[['adj open', 'adj high', 'adj low', '5. adjusted close', '6. volume']]
        data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

        data_list.append((data, symbol))

    return data_list


class RebalanceStrategy(bt.Strategy):
    params = (('assets', list()),
              ('rebalance_months', [1, 6]),)  # Float: 1 == 100%

    def __init__(self):
        self.rebalance_dict = dict()
        for i, d in enumerate(self.datas):
            self.rebalance_dict[d] = dict()
            self.rebalance_dict[d]['rebalanced'] = False
            for asset in self.p.assets:
                if asset[0] == d._name:
                    self.rebalance_dict[d]['target_percent'] = asset[1]

    def next(self):
        print(self.datas[0].datetime.datetime())
        print("next()")

        for i, d in enumerate(self.datas):
            dt = d.datetime.datetime()
            dn = d._name
            pos = self.getposition(d).size

            if dt.month in self.p.rebalance_months and self.rebalance_dict[d]['rebalanced'] == False:
                print('{} Sending Order: {} | Month {} | Rebalanced: {} | Pos: {}'.format(dt, dn, dt.month,
                                                                                          self.rebalance_dict[d][
                                                                                              'rebalanced'], pos))
                self.order_target_percent(d, target=self.rebalance_dict[d]['target_percent'] / 100)
                self.rebalance_dict[d]['rebalanced'] = True

            # Reset
            if dt.month not in self.p.rebalance_months:
                self.rebalance_dict[d]['rebalanced'] = False

    def notify_order(self, order):
        date = self.data.datetime.datetime().date()

        if order.status == order.Completed:
            print('{} >> Order Completed >> Stock: {},  Ref: {}, Size: {}, Price: {}'.format(

                date,
                order.data._name,
                order.ref,
                order.size,
                'NA' if not order.price else round(order.price, 5)
            ))

    def notify_trade(self, trade):
        date = self.data.datetime.datetime().date()
        if trade.isclosed:
            print('{} >> Notify Trade >> Stock: {}, Close Price: {}, Profit, Gross {}, Net {}'.format(
                date,
                trade.data._name,
                trade.price,
                round(trade.pnl, 2),
                round(trade.pnlcomm, 2)))

if __name__ == "__main__":
    startcash = 10000

    # Create an instance of cerebro
    cerebro = bt.Cerebro()

    # strategy Params
    strat_params = [
        ('spy', 60),
        ('tlt', 40),
    ]

    symbol_list = [x[0] for x in strat_params]
    print(symbol_list)

    # Add our strategy
    cerebro.addstrategy(RebalanceStrategy, assets=strat_params)

    start = datetime(2010, 1, 1)
    end = datetime(2019, 1, 1)
    spy = bt.feeds.YahooFinanceData(dataname="spy", fromdate=start, todate=end)
    tlt = bt.feeds.YahooFinanceData(dataname="tlt", fromdate=start, todate=end)

    # Add the data to Cerebro
    cerebro.adddata(spy)
    cerebro.adddata(tlt)

    # Set our desired cash start
    cerebro.broker.setcash(startcash)
    cerebro.broker.set_checksubmit(False)


    cerebro.addanalyzer(bt.analyzers.SharpeRatio, riskfreerate=0.0)
    cerebro.addanalyzer(bt.analyzers.Returns)
    cerebro.addanalyzer(bt.analyzers.DrawDown)

    # Run over everything
    results = cerebro.run()

    # Get final portfolio Value
    portvalue = cerebro.broker.getvalue()
    pnl = portvalue - startcash

    # Print out the final result
    print('Final Portfolio Value: ${}'.format(portvalue))
    print('P/L: ${}'.format(pnl))
    # Finally plot the end results

    analyzers = results[0].analyzers
    mdd = analyzers.drawdown.get_analysis()['max']['drawdown'],
    cagr = analyzers.returns.get_analysis()['rnorm100'],
    sharp = analyzers.sharperatio.get_analysis()['sharperatio']
    print(mdd, cagr, sharp)

    cerebro.plot(style='candlestick')

    print("done")

