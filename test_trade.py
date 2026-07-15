from portfolio import Portfolio
from trade_engine import TradeEngine


account = Portfolio(100)


engine = TradeEngine(
    account
)


engine.execute(
    "England World Cup",
    "NO",
    5
)


engine.settle(
    "WIN",
    4
)


account.report()