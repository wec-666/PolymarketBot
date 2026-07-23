import sqlite3
from risk_manager import (
    calculate_position,
    check_position
)
from database import (
    save_open_trade,
    close_trade_record
)

import time


DB_NAME = "polymarket_bot.db"



def get_price_history(
    market_id
):

    conn = sqlite3.connect(
        DB_NAME
    )

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT
        market_id,
        yes_price,
        no_price,
        created_at

        FROM market_snapshots

        WHERE market_id = ?

        ORDER BY created_at ASC
        """,
        (
            market_id,
        )
    )


    rows = cursor.fetchall()


    conn.close()


    return rows



if __name__ == "__main__":

    data = get_price_history(
        "558934"
    )


    for item in data[:10]:

        print(item)
def simulate_position(
    prices,
    direction="YES",
    capital=100
):


    buy_price = None
    amount = calculate_position(
    capital
)


    print(
        "投入资金:",
        amount
    )


    for item in prices:


        yes_price = item[1]
        no_price = item[2]


        if buy_price is None:


            if direction == "YES":

                buy_price = yes_price

            else:

                buy_price = no_price


            print(
                "开仓价格:",
                buy_price
            )
            amount = calculate_position(
                capital
            )


            shares = amount / buy_price


            save_open_trade(
                "558934",
                "BUY_YES",
                amount,
                buy_price,
                shares,
                time.time()
            )

            continue



        if direction == "YES":

            current_price = yes_price

        else:

            current_price = no_price



        profit_percent = (
            (current_price - buy_price)
            /
            buy_price
            *
            100
        )


        print(
            "当前价格:",
            current_price,
            "收益:",
            round(
                profit_percent,
                2
            ),
            "%"
        )


    status = check_position(
        profit_percent,
        take_profit=1,
        stop_loss=-10
    )

    print(
        "风控状态:",
        status
    )


    if status == "TAKE_PROFIT":

        print(
            "触发止盈"
        )

        profit = amount * (
            profit_percent / 100
        )


        close_trade_record(
            "558934",
            "BUY_YES",
            current_price,
            time.time(),
            profit,
            profit_percent,
            "TAKE_PROFIT"
        )


    return profit_percent

    if status == "STOP_LOSS":

        print(
            "触发止损"
        )


        profit = amount * (
            profit_percent / 100
        )


        close_trade_record(
            "558934",
            "BUY_YES",
            current_price,
            time.time(),
            profit,
            profit_percent,
            "STOP_LOSS"
        )


        return profit_percent

    print(
        "没有触发退出"
    )


    return profit_percent
if __name__ == "__main__":


    data = get_price_history(
        "558934"
    )


    result = simulate_position(
        data,
        "YES"
    )


    print(
        "最终收益:",
        result
    )