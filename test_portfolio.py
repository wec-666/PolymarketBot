from portfolio import Portfolio



account = Portfolio(
    100
)



account.open_trade(

    "Argentina World Cup",

    5,

    "NO"

)



account.close_trade(

    "WIN",

    10

)



account.report()