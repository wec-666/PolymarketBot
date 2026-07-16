import json



def generate_signal(
    probability,
    volume,
    score
):


    if isinstance(probability, str):

        probability=json.loads(probability)



    yes=float(probability[0])

    no=float(probability[1])



    yes_percent=yes*100

    no_percent=no*100





    # ======================
    # 极端市场过滤
    # ======================

    if yes_percent >=95 or no_percent >=95:

        return "AVOID"





    # ======================
    # 流动性过滤
    # ======================

    if volume < 5000000:

        return "AVOID"






    # ======================
    # 强交易机会
    # ======================


    if score >=80 and volume >=50000000:



        if 55 <= yes_percent <=75:


            return "BUY_YES"




        if 55 <= no_percent <=75:


            return "BUY_NO"






    # ======================
    # 普通观察
    # ======================

    if score >=65:

        return "HOLD"



    return "AVOID"