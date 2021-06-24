import datetime
import backtrader as bt
from pandas_datareader import data
import yfinance
yfinance.pdr_override()


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
        # print(self.datas[0].datetime.datetime())
        # print("next()")

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


def apply_adj_stock(df):
    adj_ratio = df["Adj Close"] / df["Close"]
    df["Open"] = df["Open"] * adj_ratio
    df["High"] = df["High"] * adj_ratio
    df["Low"] = df["Low"] * adj_ratio
    df["Close"] = df["Close"] * adj_ratio
    return df


if __name__ == '__main__':
    df_tlt = apply_adj_stock(data.get_data_yahoo("TLT"))
    df_spy = apply_adj_stock(data.get_data_yahoo("SPY"))

    fromdate = datetime.datetime(2005, 1, 1)
    todate = datetime.datetime(2020, 12, 31)

    # dataname="spy"
    data_tlt = bt.feeds.PandasData(dataname=df_tlt, fromdate=fromdate, todate=todate)
    data_spy = bt.feeds.PandasData(dataname=df_spy, fromdate=fromdate, todate=todate)

    cerebro = bt.Cerebro()
    cerebro.adddata(data_tlt, name="tlt")
    cerebro.adddata(data_spy, name="spy")

    # Add our strategy
    strat_params = [('spy', 60), ('tlt', 40)]
    cerebro.addstrategy(RebalanceStrategy, assets=strat_params)

    # Set our desired cash start
    startcash = 10000
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

