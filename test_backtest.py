from backtest import simulate_trade, calculate_profit


probability = '["0.22","0.78"]'


score = 100


volume = 100000000


trade = simulate_trade(
    probability,
    score,
    volume
)


print("模拟交易方向:")
print(trade)



result = "NO"


profit = calculate_profit(
    trade,
    result
)


print("模拟收益:")
print(profit,"%")