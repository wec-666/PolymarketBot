import json
from trade_signal import generate_signal


def calculate_score(probability, volume):

    if isinstance(probability, str):
        probability = json.loads(probability)


    yes = float(probability[0]) * 100


    score = 50


    # 概率优势

    if yes >= 70 or yes <= 30:
        score += 30

    elif yes >= 55 or yes <=45:
        score += 15


    # 交易量

    if volume >= 100000000:
        score += 20

    elif volume >= 50000000:
        score += 10


    if score > 100:
        score = 100


    return score



def show_top_markets(markets):


    market_list = []


    for market in markets:

        probability = market.get("outcomePrices")

        volume = float(
            market.get("volume",0)
        )


        score = calculate_score(
            probability,
            volume
        )


        market_list.append(
            {
                "market": market,
                "score": score
            }
        )


    market_list.sort(
        key=lambda x:x["score"],
        reverse=True
    )


    print()
    print("🔥 AI重点关注市场")
    print("====================")


    for i,item in enumerate(
        market_list[:5],
        start=1
    ):

        market=item["market"]

        probability=market.get(
            "outcomePrices"
        )

        volume=float(
            market.get("volume",0)
        )


        score=item["score"]


        signal=generate_signal(
            probability,
            volume,
            score
        )


        print()

        print("排名:",i)

        print(
            "市场:",
            market.get("question")
        )

        print(
            "评分:",
            score
        )

        print(
            "交易量:",
            volume
        )

        print(
            "概率:",
            probability
        )

        print(
            "交易信号:",
            signal
        )
    return market_list[:5]