from api_client import get_markets
from scanner import show_top_markets
from portfolio import Portfolio
from trade_engine import TradeEngine
from trade_signal import generate_signal



print("======================")
print("🤖 Polymarket AI Bot启动")
print("======================")


# 创建资金账户

account = Portfolio(100)


# 创建交易引擎

engine = TradeEngine(account)



# 获取市场

markets = get_markets()


print()

print(
    "获取市场数量:",
    len(markets)
)


print()


# 扫描市场

top_markets = show_top_markets(markets)
print()

print("======================")
print("🤖 自动交易检测")
print("======================")


for item in top_markets:


    market = item["market"]

    score = item["score"]


    probability = market.get(
        "outcomePrices"
    )


    volume = float(
        market.get("volume",0)
    )


    signal = generate_signal(
        probability,
        volume,
        score
    )


    if signal == "BUY_NO":

        print("发现交易机会:")
        print(market.get("question"))
        print("信号:", signal)


        engine.execute(

            market.get("question"),

            "NO",

            5

        )


        break


    elif signal == "BUY_YES":

        print("发现交易机会:")
        print(market.get("question"))
        print("信号:", signal)


        engine.execute(

            market.get("question"),

            "YES",

            5

        )


        break
print()

print("======================")
print("🤖 自动交易检测")
print("======================")


for market in markets:


    score = market.get("score",0)


    signal = market.get("signal")


    if score >= 90:


        print(
            "发现高评分市场:",
            market.get("question")
        )


        engine.execute(

            market.get("question"),

            "NO",

            5

        )


        break



account.report()