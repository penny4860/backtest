import pandas as pd


def returns(prices: pd.Series):
    # 시작일에 대한 상대적 가격
    return (1 + prices.pct_change(1)).cumprod()


def drawdown(prices: pd.Series):
    rets = returns(prices)
    return (rets.div(rets.cummax()) - 1) * 100


def cagr(prices):
    # 연평균 수익률
    delta = (prices.index[-1] - prices.index[0]).days / 365.25
    return ((prices[-1] / prices[0]) ** (1 / delta) - 1) * 100
