import pandas as pd


if __name__ == "__main__":
    s = "2000-01-01"
    e = "2020-07-07"
    dates = pd.date_range(s, e)
    df = pd.DataFrame(index=dates)

    df_tmp = pd.read_csv("../datas/KOSPI200.csv", usecols=["Date", "Price"])
    df_tmp = df_tmp.set_index("Date")
    df = df.join(df_tmp)
    df = df.dropna()
    print(df)

