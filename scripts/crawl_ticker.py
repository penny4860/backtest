import pandas_datareader.data as web
import datetime


if __name__ == "__main__":
    # 1. get raw data
    start = datetime.datetime(1970, 1, 1)
    end = datetime.datetime(2019, 1, 1)
    spy = web.DataReader("USDKRW=x", "yahoo", start, end)["Adj Close"]
    print(spy)

