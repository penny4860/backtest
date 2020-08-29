from src.pv import Asset, Agent
import matplotlib.pyplot as plt


# 환헤지 : to_krw=False
if __name__ == "__main__":
    # 주식 단기채 중기채 금

    spy = Asset.from_yahoo("SPY", to_krw=True)
    ief = Asset.from_yahoo("IEF", to_krw=True)
    tlt = Asset.from_yahoo("TLT", to_krw=True)
    iau = Asset.from_yahoo("IAU", to_krw=True)
    kodex_gold = Asset.from_fdr("132030", to_krw=False)

    assets = [spy, ief, tlt, iau, kodex_gold]
    agent = Agent(assets=assets, ratios=[0.3, 0.15, 0.4, 0.15, 0.0])
    agent.corr()

    df = agent.run(60)
    df.plot()
    plt.show()

# [Portfolio]::2010-10-01~2020-08-28::Final Balance: 243238274, CAGR: 9.4%, MDD: -11.6%
# [SPY]::2010-10-01~2020-08-28::Final Balance: 388034309, CAGR: 14.7%, MDD: -29.7%
# [IEF]::2010-10-01~2020-08-28::Final Balance: 156631902, CAGR: 4.6%, MDD: -18.0%
# [TLT]::2010-10-01~2020-08-28::Final Balance: 211236255, CAGR: 7.8%, MDD: -27.3%
# [IAU]::2010-10-01~2020-08-28::Final Balance: 149632151, CAGR: 4.3%, MDD: -41.5%
# [132030]::2010-10-01~2020-08-28::Final Balance: 134417200, CAGR: 3.0%, MDD: -44.9%


# [IAU]::2010-10-01~2019-03-11::Final Balance: 96684506, CAGR: -0.5%, MDD: -41.5%
# [132030]::2010-10-01~2019-03-11::Final Balance: 94047025, CAGR: -0.7%, MDD: -44.9%
