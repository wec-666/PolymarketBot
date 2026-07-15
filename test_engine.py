from backtest_engine import run_backtest


markets = [

    {
        "question":
        "Argentina",

        "outcomePrices":
        '["0.20","0.80"]',

        "volume":
        100000000,

        "score":
        100,

        "result":
        "NO"
    },


    {
        "question":
        "Spain",

        "outcomePrices":
        '["0.58","0.42"]',

        "volume":
        90000000,

        "score":
        85,

        "result":
        "YES"
    },


    {
        "question":
        "Bitcoin",

        "outcomePrices":
        '["0.50","0.50"]',

        "volume":
        1000000,

        "score":
        50,

        "result":
        "YES"
    }

]


run_backtest(markets)