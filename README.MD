
## 질문

* 리밸런싱 예제코드에서 SPY/TLT로 바꾸니까 결과가 이상하다. 왜 이러지?
* 리밸런싱 예제코드분석
* 리밸런싱 예제코드에 csv 데이터 넣어서 도는것 확인해보자.


## 내용

* Strategy class 구현
    1) ```__init__()```
    2) ```next()```
        * 조건에 따라서 ```buy(), sell()``` 을 호출
    3) notify_order()
    4) notify_trade()
* Driver 구현
    1) Celebro 객체
    2) c.addstrategy()
    3) c.adddata(d)
    4) c.addsizer()
    5) c.run()
* 자산배분 & 리밸런싱 예제
    * https://backtest-rookies.com/2020/05/09/backtrader-portfolio-rebalancing-with-alpha-vantage/
    * https://teddykoker.com/2019/04/backtesting-portfolios-of-leveraged-etfs-in-python-with-backtrader/
        * SPY / TLT로 바꿔서 해봤는데 결과가 좀 이상함.