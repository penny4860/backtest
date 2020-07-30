import FinanceDataReader as fdr

df = fdr.DataReader('USD/KRW', '1990')[["Close"]]
df.columns = ["Price"]


def usd2krw(df):
    df_usd2krw = fdr.DataReader('USD/KRW', '1990')[["Close"]]
    df_usd2krw.columns = ["usd2krw"]
    df = df.join(df_usd2krw)
    df = df.dropna()
    df["Price"] = df["Price"] * df["usd2krw"]
    df = df[["Price"]]
    return df


if __name__ == "__main__":
    from src.pv import Asset
    spy = Asset.from_yahoo("SPY", "USD")
    print(usd2krw(spy.df))

