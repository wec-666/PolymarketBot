from backtest import simulate_trade, calculate_profit
from database import get_connection
def get_snapshot_history():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM market_snapshots
        ORDER BY id DESC
        LIMIT 10
        """
    )

    data = cursor.fetchall()

    connection.close()

    return data


def run_backtest(markets):

    initial_money = 100

    money = initial_money

    total_trade = 0
    win = 0
    lose = 0


    print("======================")
    print("🔥 回测开始")
    print("======================")


    for market in markets:

        probability = market.get("outcomePrices")

        volume = float(
            market.get("volume", 0)
        )


        score = market.get(
            "score",
            0
        )


        # 模拟交易方向

        position = simulate_trade(
            probability,
            score,
            volume
        )


        if position == "WAIT":
            continue


        total_trade += 1


        # 这里暂时模拟真实结果
        # 后面会接入历史结果数据

        result = market.get(
            "result",
            "NO"
        )


        profit = calculate_profit(
            position,
            result
        )


        money = money + (
            money * profit / 100
        )


        if profit > 0:

            win += 1

        else:

            lose += 1



    print()

    print("🔥 回测报告")

    print("----------------------")

    print(
        "初始资金:",
        "$",
        initial_money
    )


    print(
        "最终资金:",
        "$",
        round(money,2)
    )


    print(
        "交易次数:",
        total_trade
    )


    print(
        "盈利次数:",
        win
    )


    print(
        "亏损次数:",
        lose
    )


    if total_trade > 0:

        win_rate = (
            win / total_trade
        ) * 100

        print(
            "胜率:",
            round(win_rate,2),
            "%"
        )

    else:

        print(
            "没有触发交易"
        )


    print("======================")