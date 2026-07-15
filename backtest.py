import json


def simulate_trade(
    probability,
    score,
    volume
):

    if isinstance(probability, str):
        probability = json.loads(probability)


    yes = float(probability[0]) * 100


    # 交易规则

    if score >= 85 and volume >= 50000000:

        if yes >= 60:

            position = "YES"

        elif yes <= 40:

            position = "NO"

        else:

            position = "WAIT"

    else:

        position = "WAIT"


    return position



def calculate_profit(
    position,
    result
):

    if position == "WAIT":

        return 0


    if position == result:

        return 10


    else:

        return -10