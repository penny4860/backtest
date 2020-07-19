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


def sim_leverage(proxy, leverage=1, expense_ratio=0.0, initial_value=1.0):
    """leverage와 보수율을 시뮬레이션

    :param proxy:
    :param leverage:
    :param expense_ratio:
        1년 보수율
    :param initial_value:
    :return:
    """
    # 날짜별 percent change
    pct_change = proxy.pct_change(1)
    pct_change = (pct_change - expense_ratio / 252) * leverage

    # 시작일대비 percent change
    sim = (1 + pct_change).cumprod() * initial_value
    sim[0] = initial_value
    return sim
