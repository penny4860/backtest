from src.pv import Asset, Agent
import matplotlib.pyplot as plt


# 환헤지 : to_krw=False
if __name__ == "__main__":
    # kospi = Asset.from_investing_csv("KOSPI", "./datas/KOSPI200.csv", to_krw=False)
    # spy = Asset.from_yahoo("SPY", to_krw=True)
    iau = Asset.from_yahoo("IAU", to_krw=True)
    kodex_gold = Asset.from_fdr("132030", to_krw=False)

    assets = [iau, kodex_gold]
    agent = Agent(assets=assets, ratios=[0.5, 0.5])
    agent.corr()

    df = agent.run(120)
    df.plot()
    plt.show()
