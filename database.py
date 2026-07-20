import sqlite3


DATABASE_NAME = "polymarket_bot.db"


def get_connection():

    connection = sqlite3.connect(
        DATABASE_NAME
    )

    connection.row_factory = sqlite3.Row

    return connection


def create_tables():

    connection = get_connection()

    cursor = connection.cursor()

    # ======================
    # 市场快照表
    # ======================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS market_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market_id TEXT,
            question TEXT NOT NULL,
            yes_price REAL,
            no_price REAL,
            volume REAL,
            score REAL,
            signal TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS account_history (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        balance REAL,

        equity REAL,

        invested REAL,

        position_count INTEGER,

        realized_profit REAL,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS account_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            balance REAL,
            equity REAL,
            invested REAL,
            position_count INTEGER,
            realized_profit REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # ======================
    # 交易记录表
    # ======================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market TEXT NOT NULL,
            direction TEXT NOT NULL,
            amount REAL NOT NULL,
            open_price REAL NOT NULL,
            shares REAL NOT NULL,
            open_time REAL NOT NULL,
            close_price REAL,
            close_time REAL,
            profit REAL,
            profit_percent REAL,
            close_reason TEXT,
            status TEXT NOT NULL
        )
        """
    )

    # ======================
    # 账户快照表
    # ======================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS account_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            balance REAL NOT NULL,
            invested_capital REAL NOT NULL,
            position_count INTEGER NOT NULL,
            realized_profit REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    try:
        cursor.execute(
            """
            ALTER TABLE trades
            ADD COLUMN snapshot_id INTEGER
            """
        )

    except Exception:
        pass
    connection.commit()
    connection.close()

    print(
        "✅ SQLite数据库和数据表创建成功"
    )


# ======================
# 保存开仓记录
# ======================

def save_open_trade(
    market,
    direction,
    amount,
    open_price,
    shares,
    open_time,
    snapshot_id=None
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO trades (
            market,
            direction,
            amount,
            open_price,
            shares,
            open_time,
            status
            snapshot_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            market,
            direction,
            amount,
            open_price,
            shares,
            open_time,
            "OPEN",
            snapshot_id
        )
    )

    connection.commit()
    connection.close()

    print(
        "✅ 开仓记录已保存到数据库"
    )


# ======================
# 更新平仓记录
# ======================

def close_trade_record(
    market,
    direction,
    close_price,
    close_time,
    profit,
    profit_percent,
    close_reason
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM trades
        WHERE market = ?
          AND direction = ?
          AND status = 'OPEN'
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            market,
            direction
        )
    )

    trade = cursor.fetchone()

    if trade is None:

        connection.close()

        print(
            "⚠️ 数据库中没有找到对应的OPEN交易"
        )

        return False

    cursor.execute(
        """
        UPDATE trades
        SET close_price = ?,
            close_time = ?,
            profit = ?,
            profit_percent = ?,
            close_reason = ?,
            status = 'CLOSED'
        WHERE id = ?
        """,
        (
            close_price,
            close_time,
            profit,
            profit_percent,
            close_reason,
            trade["id"]
        )
    )

    connection.commit()
    connection.close()

    print(
        "✅ 平仓记录已更新到数据库"
    )

    return True


# ======================
# 保存市场快照
# ======================

def save_market_snapshot(
    market_id,
    question,
    yes_price,
    no_price,
    volume,
    score,
    signal
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO market_snapshots (
            market_id,
            question,
            yes_price,
            no_price,
            volume,
            score,
            signal
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            market_id,
            question,
            yes_price,
            no_price,
            volume,
            score,
            signal
        )
    )

    connection.commit()

    snapshot_id = cursor.lastrowid

    connection.close()

    return snapshot_id
def get_market_snapshot(snapshot_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM market_snapshots
        WHERE id = ?
        """,
        (
            snapshot_id,
        )
    )

    snapshot = cursor.fetchone()

    connection.close()

    return snapshot


# ======================
# 保存账户快照
# ======================

def save_account_snapshot(
    balance,
    invested_capital,
    position_count,
    realized_profit
):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO account_snapshots
        (
            balance,
            invested_capital,
            position_count,
            realized_profit
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            balance,
            invested_capital,
            position_count,
            realized_profit
        )
    )

    connection.commit()

    connection.close()

    print(
        "✅ 账户快照已保存到数据库"
    )



def save_account_history(
    balance,
    equity,
    invested,
    position_count,
    realized_profit
):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        INSERT INTO account_history
        (
            balance,
            equity,
            invested,
            position_count,
            realized_profit
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            balance,
            equity,
            invested,
            position_count,
            realized_profit
        )
    )


    connection.commit()

    connection.close()
    print(
    "✅ 账户历史已保存到数据库"
)



if __name__ == "__main__":

    create_tables()