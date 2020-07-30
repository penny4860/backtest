from src.pv import Asset, Agent


if __name__ == "__main__":
    spy = Asset.from_yahoo("SPY")
    tlt = Asset.from_yahoo("TLT")
    kospi = Asset.from_investing_csv("KOPSI", "./datas/KOSPI200.csv")

    agent = Agent(assets=[spy, tlt], ratios=[0.6, 0.4])
    returns = agent.run(60)

    agent = Agent(assets=[spy, kospi, tlt], ratios=[0.3, 0.3, 0.4])
    returns = agent.run(60)

