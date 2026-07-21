import json
from trade_signal import generate_signal
from news_engine import NewsEngine
from database import save_market_snapshot



def calculate_score(probability, volume):


    if isinstance(probability, str):

        probability = json.loads(probability)


    yes = float(probability[0]) * 100


    score = 50


    # 概率优势

    if yes >= 70 or yes <= 30:

        score += 30


    elif yes >=55 or yes <=45:

        score +=15



    # 交易量

    if volume >=100000000:

        score +=20


    elif volume >=50000000:

        score +=10



    if score >100:

        score=100


    return score





def scan_markets(markets):


    results=[]

    news_engine = NewsEngine()



    for market in markets:



        probability = market.get(
            "outcomePrices"
        )
        if isinstance(probability, str):

            probability = json.loads(probability)


        if not probability:

            continue




        volume=float(
            market.get(
                "volume",
                0
            )
        )



        score=calculate_score(

            probability,

            volume

        )
        news_result = news_engine.analyze_news(

            market.get(
                "question",
                ""

            )

)



        news_impact = news_result.get(

            "adjustment",

            0

)



        score += news_impact



        if score > 100:

            score = 100


        if score < 0:

            score = 0


        if score > 100:

            score = 100


        if score < 0:

            score = 0



        signal=generate_signal(

            probability,

            volume,

            score

        )

    save_market_snapshot(

        market.get(
            "id"
        ),

        market.get(
            "question"
        ),

        float(
            probability[0]
        ),

        float(
            probability[1]
        ),

    volume,

    score,

    signal

)
    results.append(

            {

                "market": market,

                "score": score,

                "signal": signal,

                "news": news_result,

                "news_impact": news_impact

            }

)



    return results







def show_top_markets(markets):



    results=scan_markets(markets)



    results.sort(

        key=lambda x:x["score"],

        reverse=True

    )




    print()

    print("🔥 AI重点关注市场")

    print("====================")




    for i,item in enumerate(
        results[:5],
        start=1
    ):



        market=item["market"]



        print()

        print(
            "排名:",
            i
        )


        print(
            "市场:",
            market.get("question")
        )


        print(
            "评分:",
            item["score"]
        )


        print(
            "交易信号:",
            item["signal"]
        )



    return results