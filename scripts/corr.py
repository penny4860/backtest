import pandas as pd
from pandas_datareader import data
import yfinance
yfinance.pdr_override()

# TIGER 200 (102110.KS) : 20%
# KODEX 골드선물 (132030.KS) : 10%
# KOSEF 국고채 10년 (148070.KS)
TICKERS = ["102110.KS", "DIA", "QQQ", "SPY", 'IEF', 'TLT', "132030.KS", "148070.KS"]
TICKERS = ["102110.KS", "133690.KS", "148070.KS"]
TICKERS = ['LTPZ', 'EDV', "SPY"]

if __name__ == "__main__":
    s = "2000-01-01"
    e = "2020-07-07"
    dates = pd.date_range(s, e)

    df = pd.DataFrame(index=dates)
    for ticker in TICKERS:
        df_tmp = data.get_data_yahoo(ticker, s)
        df_tmp = df_tmp[["Adj Close"]]
        df_tmp = df_tmp.rename(columns={"Adj Close": ticker})
        df = df.join(df_tmp)
        df = df.dropna()
    df = df / df.iloc[0]
    # print(df.head())
    import matplotlib.pyplot as plt
    df.plot()
    plt.show()

    daily_returns = df.copy()
    daily_returns[1:] = (df[1:] / df[:-1].values) - 1
    daily_returns.iloc[0] = 0
    print(daily_returns.corr(method="pearson"))