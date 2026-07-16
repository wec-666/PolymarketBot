from risk_manager import (
    calculate_position,
    check_risk,
    check_position
)



print(
    "仓位:",
    calculate_position(100)
)



print(
    "风险:",
    check_risk(2)
)



print(
    "盈利:",
    check_position(25)
)



print(
    "亏损:",
    check_position(-15)
)



print(
    "正常:",
    check_position(5)
)