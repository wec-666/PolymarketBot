import json


def generate_signal(
    probability,
    volume,
    score
):

    if isinstance(probability, str):
        probability = json.loads(probability)

    yes = float(probability[0]) * 100


    if (
        score >= 85
        and volume >= 50000000
        and (yes >= 60 or yes <= 40)
    ):

        signal = "🟢 WATCH"


    elif score >= 70:

        signal = "🟡 HOLD"


    else:

        signal = "🔴 AVOID"


    return signal