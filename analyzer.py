import ast


def analyze_market(question, probability, volume):

    probability = ast.literal_eval(probability)

    yes = float(probability[0]) * 100
    volume = float(volume)


    print("========================")
    print("市场:", question)

    print("Yes概率:", round(yes,2), "%")
    print("交易量:", round(volume,2))


    # 方向判断
    if yes >= 55:
        print("方向判断: 市场明显偏向 Yes")

    elif yes <= 45:
        print("方向判断: 市场明显偏向 No")

    else:
        print("方向判断: 双方接近，市场观望")


    # 风险分析
    if 45 <= yes <= 55:
        risk = "高风险（双方接近）"

    elif yes >= 70 or yes <= 30:
        risk = "低风险（市场倾向明显）"

    else:
        risk = "中等风险"


    print("风险等级:", risk)