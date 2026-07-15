import json


def ai_market_report(
    question,
    probability,
    volume,
    risk
):

    if isinstance(probability, str):
        probability = json.loads(probability)


    yes = float(probability[0]) * 100


    print("======================")
    print("🤖 AI市场分析报告")


    print("市场:")
    print(question)


    print()

    print("Yes概率:")
    print(f"{yes:.2f}%")


    print()

    print("交易量:")
    print(f"{volume:.2f}")


    print()


    if yes >= 70:

        opinion = "市场明显偏向 Yes"

    elif yes <= 30:

        opinion = "市场明显偏向 No"

    else:

        opinion = "双方概率接近，需要观察"


    print("AI判断:")
    print(opinion)


    print()

    print("风险:")
    print(risk)


    if volume >= 50000000:

        advice = "高交易量市场，值得持续跟踪"

    else:

        advice = "等待更多市场信号"


    print()

    print("AI建议:")
    print(advice)


    print("======================")