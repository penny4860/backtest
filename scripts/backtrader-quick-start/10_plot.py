from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt


# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (
        ('maperiod', 15),
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # 각 line의 종가를 tracking
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Simple Moving Average indicator : 거래 로직의 지표 (indicator)
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0],
            period=self.params.maperiod
        )

        # Indicators for the plotting show
        # bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        # bt.indicators.WeightedMovingAverage(self.datas[0], period=25,
        #                                     subplot=True)
        # bt.indicators.StochasticSlow(self.datas[0])
        # bt.indicators.MACDHisto(self.datas[0])
        # rsi = bt.indicators.RSI(self.datas[0])
        # bt.indicators.SmoothedMovingAverage(rsi, period=10)
        # bt.indicators.ATR(self.datas[0], plot=False)

    def notify_order(self, order):
        # buy, sell등의 주문이 들어왔을 떄 실행하는 함수

        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # 주문이 완료되었으면 관련 로그를 출력
        if order.status in [order.Completed]:
            price = order.executed.price
            cost = order.executed.value
            commision = order.executed.comm

            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {price}, Cost: {cost}, Comm {commision}')

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log(f'SELL EXECUTED, Price: {price}, Cost: {cost}, Comm {commision}')

            self.bar_executed = len(self)

        # 주문이 실패
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        # Sell 주문이 완료되면 실행
        if not trade.isclosed:
            return
        self.log(f'OPERATION PROFIT, GROSS {trade.pnl:.2f}, NET {trade.pnlcomm:.2f}')

    def next(self):
        # 1. 현재 종가를 출력
        #   [0] : 현재
        cash = self.broker.get_cash()
        value = self.broker.get_value()
        stock_value = self.broker.get_value([self.data])

        self.log(
            f'Close, {self.dataclose[0]}, Cash: {cash:.2f}, Stock: {stock_value:.2f}, Total Value: {value:.2f}'
        )

        # 2. 주문이 있는 상태 (pending)이면 종료
        if self.order:
            return

        # 시장에서 떠나 있는 상태
        if not self.position:
            # 오늘의 가격이 sma보다 높으면 매수
            if self.dataclose[0] > self.sma[0]:
                self.log(f"BUY CREATE, {self.dataclose[0]:.2f}")
                self.order = self.buy()
        else:
            # 오늘의 가격이 sma보다 낮으면 매도
            if self.dataclose[0] < self.sma[0]:
                self.log(f'SELL CREATE, {self.dataclose[0]:.2f}')
                self.order = self.sell()


if __name__ == '__main__':
    # 1. Cerebro 객체 생성
    cerebro = bt.Cerebro()

    # 2. 거래 로직을 추가
    cerebro.addstrategy(TestStrategy)

    # 3. CSV format의 데이터 추가
    data = bt.feeds.YahooFinanceCSVData(
        dataname='../../datas/orcl-1995-2014.txt',
        fromdate=datetime.datetime(2000, 1, 1),
        todate=datetime.datetime(2000, 12, 31),
        reverse=False
    )
    cerebro.adddata(data)

    # 4. 현금을 추가
    cerebro.broker.setcash(1000.0)

    # 5. 거래 단위를 추가
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    print(f'Starting Portfolio Value: {cerebro.broker.getvalue()}')

    # 6. 거래 수수로 추가
    cerebro.broker.setcommission(commission=0.0)

    # 7. Run over everything
    cerebro.run()

    # 8. Print & Plot
    print(f'Final Portfolio Value: {cerebro.broker.getvalue()}')
    cerebro.plot()

