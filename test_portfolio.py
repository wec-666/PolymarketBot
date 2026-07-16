from portfolio import Portfolio


account = Portfolio(100)



# 测试开仓

account.open_trade(

    "England World Cup",

    5,

    "BUY_NO",

    0.77

)



# 查看账户

account.report()