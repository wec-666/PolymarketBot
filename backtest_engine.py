from backtest import simulate_trade, calculate_profit
from trade_signal import generate_signal
from database import get_connection
def get_snapshot_history():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM market_snapshots
        WHERE id IN (

            SELECT MAX(id)

            FROM market_snapshots

            WHERE result IS NOT NULL

            GROUP BY market_id
        )

        OR market_id NOT IN (

            SELECT market_id

            FROM market_snapshots

            WHERE result IS NOT NULL

        )
        ORDER BY id DESC
        LIMIT 500
        """
    )

    data = cursor.fetchall()

    connection.close()

    return data


def run_backtest():
    history = get_snapshot_history()
    result_count = 0
    initial_money = 100

    money = initial_money

    signal_trade = 0

    completed_trade = 0

    win = 0

    lose = 0
    backtest_trades = []
    total_market = 0

    wait_count = 0

    avoid_count = 0


    print("======================")
    print("🔥 回测开始")
    print("======================")


    for market in history:
        market = dict(market)
        total_market += 1
        market["outcomePrices"] = [
            str(market["yes_price"]),
            str(market["no_price"])
    ]
        probability = market.get("outcomePrices")

        volume = float(
            market.get("volume", 0)
        )


        score = market.get(
            "score",
            0
        )


        # 模拟交易方向

        signal = generate_signal(
            probability,
            volume,
            score
        )

        signal_trade += 1


        # 这里暂时模拟真实结果
        # 后面会接入历史结果数据

        result = market.get(
            "result"
        )

        if result is not None:

            result_count += 1

        if result is None:

            continue


        if signal not in [
            "BUY_YES",
            "BUY_NO"
        ]:
            wait_count += 1

            continue


        completed_trade += 1


        trade_record = {

            "question": market["question"],

            "signal": signal,

            "yes_price": market["yes_price"],

            "no_price": market["no_price"],

            "result": result,

        }


        backtest_trades.append(
            trade_record
        )


        amount = money * 0.1


        profit = calculate_profit(
            amount,
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
        "产生信号:",
        signal_trade
    )


    print(
        "完成交易:",
        completed_trade
    )

    print(
        "盈利次数:",
        win
    )


    print(
        "亏损次数:",
        lose
    )


    if completed_trade > 0:

        win_rate = (
            win / completed_trade
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

    print(
    "扫描市场:",
    total_market
)
    print(
    "有结果市场:",
    result_count
)
    print()

    print(
        "🔥 回测交易明细"
    )

    print(
        "------------------"
    )


    for trade in backtest_trades:

        print(
            trade
    )

    print(
    "等待数量:",
    wait_count
)
    print("======================")