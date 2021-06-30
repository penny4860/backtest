import pandas as pd


def returns(prices: pd.Series):
    # 시작일에 대한 상대적 가격
    return (1 + prices.pct_change(1)).cumprod()


def drawdown(prices: pd.Series):
    rets = returns(prices)
    dd = (rets.div(rets.cummax()) - 1) * 100
    return dd.min()


def cagr(prices: pd.Series):
    # 연평균 수익률
    delta = (prices.index[-1] - prices.index[0]).days / 365.25
    return ((prices[-1] / prices[0]) ** (1 / delta) - 1) * 100


def fdr2backtrader(df):
    """FinanceDataReader package로 읽어온 데이터를 Backtrader 방식으로 변환하는 함수

    # Example
        import FinanceDataReader as fdr
        df = fdr.DataReader('SPY')
        df = fdr2backtrader(df)
    """
    df = df[["Open", "High", "Low", "Close", "Volume"]]
    return df


def apply_adj_close_stock(df: pd.DataFrame):
    # 데이터를 수정 종가기준으로 보정해주는 함수
    # df.columns : [Open, High, Low, Close, Adj Close]
    adj_ratio = df["Adj Close"] / df["Close"]
    df["Open"] = df["Open"] * adj_ratio
    df["High"] = df["High"] * adj_ratio
    df["Low"] = df["Low"] * adj_ratio
    df["Close"] = df["Close"] * adj_ratio
    return df
