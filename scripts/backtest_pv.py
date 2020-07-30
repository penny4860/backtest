from src.pv import Asset, Agent


if __name__ == "__main__":
    spy = Asset.from_yahoo("SPY")
    tlt = Asset.from_yahoo("TLT")

    agent = Agent(assets=[spy, tlt], ratios=[0.5, 0.5])
    values = agent.run(60)
    print(values.iloc[-2])
    # 2020-07-29  49157.654274

    agent = Agent(assets=[spy, tlt], ratios=[0.7, 0.3])
    values = agent.run(60)
    print(values.iloc[-2])
    # 2020-07-29  51076.710552

