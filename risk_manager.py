def calculate_position(
    capital,
    risk_percent=5
):

    """
    计算单次投入资金
    """

    position = capital * (
        risk_percent / 100
    )


    return round(
        position,
        2
    )





def check_risk(
    consecutive_losses,
    max_loss=3
):

    """
    连续亏损检查
    """


    if consecutive_losses >= max_loss:

        return "STOP"


    return "CONTINUE"






def check_position(
    profit_percent,
    take_profit=20,
    stop_loss=-10
):

    """
    持仓风险检查
    """


    if profit_percent >= take_profit:

        return "TAKE_PROFIT"



    if profit_percent <= stop_loss:

        return "STOP_LOSS"



    return "HOLD"