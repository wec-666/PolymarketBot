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

    return round(position, 2)



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



def stop_loss(
    current_loss,
    max_loss_percent=20
):
    """
    最大亏损控制
    """

    if current_loss <= -max_loss_percent:

        return True


    return False