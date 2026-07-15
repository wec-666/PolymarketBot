import requests

from ai_analyzer import ai_market_report
from scanner import show_top_markets


url = "https://gamma-api.polymarket.com/markets"


try:

    response = requests.get(
        url,
        timeout=20
    )


    markets = response.json()


except Exception as e:

    print("API连接失败:")
    print(e)

    exit()



print("🔥 热门市场 TOP 10")


markets_sorted = sorted(
    markets,
    key=lambda x:float(
        x.get("volume",0)
    ),
    reverse=True
)



for i,market in enumerate(
    markets_sorted[:10],
    start=1
):

    print("======================")

    print(
        "排名:",
        i
    )

    print(
        "标题:",
        market.get("question")
    )


    print(
        "交易量:",
        market.get("volume")
    )


    print(
        "概率:",
        market.get("outcomePrices")
    )


    ai_market_report(
        market.get("question"),
        market.get("outcomePrices"),
        float(
            market.get("volume",0)
        ),
        "自动分析"
    )



show_top_markets(markets)