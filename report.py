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


connection.close()