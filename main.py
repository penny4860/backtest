from src.pv import Asset, Agent


if __name__ == "__main__":
    spy = Asset.from_yahoo("SPY", "USD")
    tlt = Asset.from_yahoo("TLT", "USD")
    kospi = Asset.from_investing_csv("KOPSI", "./datas/KOSPI200.csv", "KRW")

    agent = Agent(assets=[spy, tlt], ratios=[0.6, 0.4])
    returns = agent.run(60)

    agent = Agent(assets=[spy, kospi, tlt], ratios=[0.3, 0.3, 0.4])
    returns = agent.run(60)

    agent = Agent(assets=[kospi, tlt], ratios=[0.6, 0.4])
    returns = agent.run(60)

    import matplotlib.pyplot as plt
    returns.plot(title="spy, kospi, tlt")
    plt.show()

