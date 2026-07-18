import sqlite3


DATABASE_NAME = "polymarket_bot.db"


connection = sqlite3.connect(
    DATABASE_NAME
)

connection.row_factory = sqlite3.Row

cursor = connection.cursor()


print("==========================")
print("📊 AI交易统计报告")
print("==========================")


# 总交易数

cursor.execute(
    """
    SELECT COUNT(*) total
    FROM trades
    """
)

total = cursor.fetchone()["total"]


# 开仓数量

cursor.execute(
    """
    SELECT COUNT(*) total
    FROM trades
    WHERE status='OPEN'
    """
)

open_count = cursor.fetchone()["total"]


# 已平仓数量

cursor.execute(
    """
    SELECT COUNT(*) total
    FROM trades
    WHERE status='CLOSED'
    """
)

closed_count = cursor.fetchone()["total"]


# 累计盈利

cursor.execute(
    """
    SELECT
    IFNULL(
        SUM(profit),
        0
    ) total_profit
    FROM trades
    """
)

profit = cursor.fetchone()["total_profit"]


print("总交易数:", total)

print("当前持仓:", open_count)

print("已平仓:", closed_count)

print("累计盈利:", round(profit, 2))
print()


# ==========================
# 盈亏统计
# ==========================


cursor.execute(
    """
    SELECT COUNT(*) total
    FROM trades
    WHERE profit > 0
    """
)

win_count = cursor.fetchone()["total"]



cursor.execute(
    """
    SELECT COUNT(*) total
    FROM trades
    WHERE profit < 0
    """
)

loss_count = cursor.fetchone()["total"]



win_rate = 0

if closed_count > 0:

    win_rate = (
        win_count / closed_count * 100
    )



cursor.execute(
    """
    SELECT
    IFNULL(
        AVG(profit),
        0
    ) avg_profit
    FROM trades
    WHERE profit > 0
    """
)

avg_profit = cursor.fetchone()["avg_profit"]



cursor.execute(
    """
    SELECT
    IFNULL(
        AVG(profit),
        0
    ) avg_loss
    FROM trades
    WHERE profit < 0
    """
)

avg_loss = cursor.fetchone()["avg_loss"]



profit_loss_ratio = 0


if avg_loss != 0:

    profit_loss_ratio = (
        avg_profit / abs(avg_loss)
    )



print(
    "盈利次数:",
    win_count
)


print(
    "亏损次数:",
    loss_count
)


print(
    "胜率:",
    round(win_rate,2),
    "%"
)


print(
    "平均盈利:",
    round(avg_profit,2)
)


print(
    "平均亏损:",
    round(avg_loss,2)
)


print(
    "盈亏比:",
    round(profit_loss_ratio,2)
)


print()

print("==========================")
print("📈 最新账户状态")
print("==========================")


cursor.execute(
    """
    SELECT *
    FROM account_snapshots
    ORDER BY id DESC
    LIMIT 1
    """
)

account = cursor.fetchone()

if account:

    print(
        "账户余额:",
        account["balance"]
    )

    print(
        "持仓资金:",
        account["invested_capital"]
    )

    print(
        "持仓数量:",
        account["position_count"]
    )

    print(
        "已实现盈亏:",
        account["realized_profit"]
    )

else:

    print(
        "暂无账户数据"
    )

print()

print("==========================")
print("📈 收益曲线分析")
print("==========================")

cursor.execute(
    """
    SELECT *
    FROM account_history
    ORDER BY id ASC
    """
)


history = cursor.fetchall()


if history:


    assets = []


    for item in history:

        assets.append(
            item["equity"]
    )


    max_asset = max(
        assets
    )


    max_drawdown = 0


    for value in assets:

        drawdown = (
            value - max_asset
        ) / max_asset * 100


        if drawdown < max_drawdown:

            max_drawdown = drawdown
    print(
        "最高资产:",
        round(max_asset,2)
    )


    print(
        "最大回撤:",
        round(max_drawdown,2),
        "%"
    )


    initial = assets[0]

    current = assets[-1]


    profit = current - initial


    rate = (
        profit / initial * 100
    )


    print(
        "历史记录:",
        len(history)
    )


    print(
        "初始资产:",
        round(initial,2)
    )


    print(
        "当前资产:",
        round(current,2)
    )


    print(
        "收益:",
        round(profit,2)
    )


    print(
        "收益率:",
        round(rate,2),
        "%"
    )


else:

    print(
        "暂无历史收益数据"
    )
    print()

print("==========================")
print("📌 当前持仓分析")
print("==========================")


import json


try:

    with open(
        "account.json",
        "r",
        encoding="utf-8"
    ) as f:

        account = json.load(f)



    positions = account.get(
        "positions",
        []
    )


    if positions:


        total_invested = 0

        max_position = 0


        for position in positions:


            amount = position.get(
                "amount",
                0
            )


            total_invested += amount


            if amount > max_position:

                max_position = amount



        print(
            "持仓数量:",
            len(positions)
        )


        print(
            "投入资金:",
            round(total_invested,2)
        )


        print(
            "最大单仓:",
            round(max_position,2)
        )


        print(
            "仓位占比:",
            round(
                total_invested /
                account.get("initial_capital",100)
                * 100,
                2
            ),
            "%"
        )


    else:

        print(
            "暂无持仓"
        )


except Exception as e:

    print(
        "持仓读取失败:",
        e
    )
    print()

print("==========================")
print("🔍 数据一致性检查")
print("==========================")


# 交易记录中的OPEN数量

cursor.execute(
    """
    SELECT COUNT(*) total
    FROM trades
    WHERE status='OPEN'
    """
)

trade_open_count = cursor.fetchone()["total"]



# 读取真实账户持仓

import json


try:

    with open(
        "account.json",
        "r",
        encoding="utf-8"
    ) as f:

        account_data = json.load(f)



    real_positions = account_data.get(
        "positions",
        []
    )


    real_position_count = len(
        real_positions
    )



    print(
        "交易记录持仓:",
        trade_open_count
    )


    print(
        "账户真实持仓:",
        real_position_count
    )



    if trade_open_count == real_position_count:

        print(
            "状态: ✅ 数据一致"
        )


    else:

        print(
            "状态: ⚠️ 存在数据差异"
        )
        print()

        print(
            "🔎 开始定位异常交易..."
        )


        # 获取数据库OPEN交易

        cursor.execute(
            """
            SELECT *
            FROM trades
            WHERE status='OPEN'
            """
        )


        open_trades = cursor.fetchall()
        print()

    print(
        "数据库OPEN交易列表:"
    )


    for trade in open_trades:

        print(
            "-",
            trade["market"],
            "|",
            trade["direction"]
    )



        # 获取账户真实市场列表

        real_markets = []


        for position in real_positions:

            real_markets.append(
                position.get("market")
            )



        for trade in open_trades:


            if trade["market"] not in real_markets:


                print()

                print(
                    "⚠️ 异常交易:"
                )


                print(
                    "市场:",
                    trade["market"]
                )


                print(
                    "方向:",
                    trade["direction"]
                )


                print(
                    "状态:",
                    trade["status"]
                )



except Exception as e:


    print(
        "检查失败:",
        e
    )
connection.close()