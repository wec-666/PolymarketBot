import json



def generate_signal(
    probability,
    volume,
    score
):


    if isinstance(probability, str):

        probability = json.loads(probability)



    yes = float(probability[0]) * 100



    # 强交易条件

    if (
        score >= 90
        and volume >= 50000000
    ):


        # YES概率过高

        if yes >= 70:

            return "BUY_YES"



        # NO概率优势

        elif yes <= 30:

            return "BUY_NO"



    # 中等机会

    if score >= 70:

        return "HOLD"



    return "AVOID"