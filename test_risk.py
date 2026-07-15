from risk_manager import (
    calculate_position,
    check_risk,
    stop_loss
)



money = 100


position = calculate_position(
    money
)


print(
    "单次投入:",
    position
)



status = check_risk(
    2
)


print(
    "交易状态:",
    status
)



stop = stop_loss(
    -25
)


print(
    "是否止损:",
    stop
)