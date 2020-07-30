import pandas as pd
from pandas_datareader import data
import yfinance
yfinance.pdr_override()

from src.utils import cagr, drawdown

TICKERS = ['TLT', "SPY"]


def common_dates(assets):
    for i, asset in enumerate(assets):
        if i == 0:
            dates = asset.df.index.copy()
        else:
            dates = dates[dates.isin(asset.df.index)]
    return dates


class Asset(object):
    def __init__(self, df, ticker, currency):
        self.ticker = ticker
        self.n_stocks = 0

        from src.currency import usd2krw
        _check_currency(currency)
        if currency == "USD":
            self.df = usd2krw(df)
        else:
            self.df = df


    @classmethod
    def from_yahoo(cls, ticker, currency):
        df = data.get_data_yahoo(ticker)[["Adj Close"]]
        df.columns = ["Price"]
        return Asset(df, ticker, currency)

    @classmethod
    def from_investing_csv(cls, ticker, csv_file, currency):
        # https://www.investing.com/ daily-csv format
        # Todo: code 정리
        s = "1900-01-01"
        e = "2200-01-01"
        dates = pd.date_range(s, e)
        df = pd.DataFrame(index=dates)

        df_tmp = pd.read_csv(csv_file, usecols=["Date", "Price"])
        df_tmp = df_tmp.set_index("Date")
        df = df.join(df_tmp)
        df = df.dropna()
        return Asset(df, ticker, currency)

    def get_price(self, d):
        return float(self.df.loc[str(d)])

    def get_value(self, d):
        return self.n_stocks * self.get_price(d)

    # Todo: 거래세, 세금 추가
    def set_value(self, d, value):
        self.n_stocks = int(value / self.get_price(d))
        remain_value = value - self.n_stocks * self.get_price(d)
        return remain_value

    def get_ticker(self):
        return self.ticker


class Agent(object):
    def __init__(self, assets, ratios=[0.5, 0.5], init_value=100000000):
        self.cash = init_value
        self.dates = common_dates(assets)
        self.assets = assets
        self.ratios = ratios

    def _get_value(self, d):
        value = self.cash
        for asset in self.assets:
            value += asset.get_value(d)
        return value

    def _rebalance(self, d):
        value = self._get_value(d)

        self.cash = 0
        for asset, ratio in zip(self.assets, self.ratios):
            target_value = value * ratio
            balance = asset.set_value(d, target_value)
            self.cash += balance

    def run(self, rebalance=60):
        # Todo : 주기를 1달단위로
        for asset in self.assets:
            asset.n_stocks = 0
        self._rebalance(self.dates[0])

        values = []
        for i, d in enumerate(self.dates):
            if rebalance is not None:
                if i % rebalance == 0:
                    self._rebalance(d)
            values.append(self._get_value(d))

        returns = pd.DataFrame(values, index=self.dates)
        final_valance = int(returns.iloc[-2, 0])
        cagr_ = cagr(returns.iloc[:, 0])
        mdd = drawdown(returns.iloc[:, 0])

        s = str(self.dates[0])[:-9]
        e = str(self.dates[-1])[:-9]

        print(f"{s}~{e}", end="::")
        print(f"Final Valance: {final_valance}, "
              f"CAGR: {cagr_:.1f}%, "
              f"MDD: {mdd:.1f}%")
        return pd.DataFrame(values, index=self.dates)


def _check_currency(currency):
    assert currency in ["USD", "KRW"]


if __name__ == "__main__":
    spy = Asset.from_yahoo("SPY")
    tlt = Asset.from_yahoo("TLT")
    agent = Agent(assets=[spy, tlt], ratios=[0.5, 0.5])
    values = agent.run(60)
    print(values)
    # 2020-07-29  49157.654274
