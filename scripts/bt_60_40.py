from src.pv import Asset, Agent
import matplotlib.pyplot as plt


if __name__ == "__main__":
    spy = Asset.from_yahoo("SPY", to_krw=False)
    tlt = Asset.from_yahoo("TLT", to_krw=False)

    assets = [spy, tlt]
    agent = Agent(assets=assets, ratios=[0.6, 0.4])
    agent.corr()

    df = agent.run(60)
    df.plot()
    plt.show()

# [Portfolio]::2002-07-30~2020-07-31::Final Valance: 506501333, CAGR: 9.5%, MDD: -30.8%
# [SPY]::2002-07-30~2020-07-31::Final Valance: 508317881, CAGR: 9.5%, MDD: -55.2%
# [TLT]::2002-07-30~2020-07-31::Final Valance: 396696496, CAGR: 8.0%, MDD: -26.6%
