import sqlite3


DB_NAME = "polymarket_bot.db"



def get_backtest_report():

    conn = sqlite3.connect(
        DB_NAME
    )

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT *
        FROM trades
        WHERE status='CLOSED'
        ORDER BY id ASC
        """
    )


    trades = cursor.fetchall()


    conn.close()


    total = len(trades)


    win = 0

    lose = 0

    total_profit = 0

    profits = []



    for trade in trades:


        profit = trade["profit"]


        if profit is None:

            continue



        total_profit += profit


        profits.append(
            profit
        )



        if profit > 0:

            win += 1


        else:

            lose += 1



    if total > 0:

        win_rate = (
            win / total
        ) * 100

    else:

        win_rate = 0



    return {

        "total_trade": total,

        "win": win,

        "lose": lose,

        "win_rate": round(
            win_rate,
            2
        ),

        "total_profit": round(
            total_profit,
            2
        )

    }





if __name__ == "__main__":


    report = get_backtest_report()


    print(
        "======================"
    )

    print(
        "🔥 回测统计报告"
    )

    print(
        "======================"
    )


    print(
        "总交易:",
        report["total_trade"]
    )


    print(
        "盈利次数:",
        report["win"]
    )


    print(
        "亏损次数:",
        report["lose"]
    )


    print(
        "胜率:",
        report["win_rate"],
        "%"
    )


    print(
        "总收益:",
        report["total_profit"]
    )