from src.pv import Asset, Agent


if __name__ == "__main__":
    spy = Asset.from_yahoo("SPY")
    tlt = Asset.from_yahoo("TLT")

    agent = Agent(assets=[spy, tlt], ratios=[0.5, 0.5])
    returns = agent.run(60)

    agent = Agent(assets=[spy, tlt], ratios=[0.7, 0.3])
    returns = agent.run(60)
    # 2020-07-29  51076.710552

