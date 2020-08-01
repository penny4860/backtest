import pandas as pd
from pandas_datareader import data
import yfinance
import numpy as np
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
    def __init__(self, df, ticker, to_krw):
        self.ticker = ticker
        self.n_stocks = 0

        from src.currency import usd2krw
        if to_krw:
            self.df = usd2krw(df)
        else:
            self.df = df

    @classmethod
    def from_yahoo(cls, ticker, to_krw):
        df = data.get_data_yahoo(ticker)[["Adj Close"]]
        df.columns = ["Price"]
        return Asset(df, ticker, to_krw)

    @classmethod
    def from_investing_csv(cls, ticker, csv_file, to_krw):
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
        return Asset(df, ticker, to_krw)

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
        self.init_value = init_value
        self.cash = init_value
        self.dates = common_dates(assets)
        self.assets = assets
        self.ratios = ratios

    def _get_value(self, d):
        value = self.cash
        for asset in self.assets:
            value += asset.get_value(d)
        return value

    def _rebalance(self, d, ratios):
        value = self._get_value(d)

        self.cash = 0
        for asset, ratio in zip(self.assets, ratios):
            target_value = value * ratio
            balance = asset.set_value(d, target_value)
            self.cash += balance

    def corr(self):
        df = pd.DataFrame(index=self.dates)
        for asset in self.assets:
            df_tmp = asset.df.copy()
            df_tmp = df_tmp.rename(columns={"Price": asset.ticker})
            df = df.join(df_tmp)
            df = df.dropna()

        df = df / df.iloc[0]
        daily_returns = df.copy()
        daily_returns[1:] = (df[1:] / df[:-1].values) - 1
        daily_returns.iloc[0] = 0
        print(daily_returns.corr(method="pearson"))
        return daily_returns

    def _run_loop(self, rebalance, ratios, title=""):
        # 초기화
        self.cash = self.init_value
        for asset in self.assets:
            asset.n_stocks = 0
        self._rebalance(self.dates[0], ratios)

        # run
        values = []
        for i, d in enumerate(self.dates):
            if rebalance is not None:
                if i % rebalance == 0:
                    self._rebalance(d, ratios)
            values.append(self._get_value(d))

        returns = pd.DataFrame(values, index=self.dates)
        final_valance = int(returns.iloc[-2, 0])
        cagr_ = cagr(returns.iloc[:, 0])
        mdd = drawdown(returns.iloc[:, 0])

        s = str(self.dates[0])[:-9]
        e = str(self.dates[-1])[:-9]

        print(f"[{title}]::{s}~{e}", end="::")
        print(f"Final Valance: {final_valance}, "
              f"CAGR: {cagr_:.1f}%, "
              f"MDD: {mdd:.1f}%")
        return returns.values

    def run(self, rebalance=60):
        values = self._run_loop(rebalance, self.ratios, "Portfolio")
        asset_values = []
        for i, asset in enumerate(self.assets):
            ratio = np.zeros_like(self.ratios)
            ratio[i] = 1.0
            asset_values.append(self._run_loop(None, ratio, asset.ticker))

        asset_values = np.array(asset_values).transpose().reshape(-1, len(self.assets))

        values = np.concatenate([values, asset_values], axis=1)
        values = values / values[0, :]
        columns = ["Portfolio"] + [asset.ticker for asset in self.assets]
        return pd.DataFrame(values, index=self.dates, columns=columns)


def _check_currency(currency):
    assert currency in ["USD", "KRW"]


if __name__ == "__main__":
    spy = Asset.from_yahoo("SPY")
    tlt = Asset.from_yahoo("TLT")
    agent = Agent(assets=[spy, tlt], ratios=[0.5, 0.5])
    values = agent.run(60)
    print(values)
    # 2020-07-29  49157.654274
