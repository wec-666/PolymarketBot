import sqlite3


DB_NAME = "polymarket_bot.db"



def update_result(
    market_id,
    result
):

    conn = sqlite3.connect(
        DB_NAME
    )

    cursor = conn.cursor()


    cursor.execute(
        """
        UPDATE market_snapshots
        SET result = ?
        WHERE market_id = ?
        """,
        (
            result,
            market_id
        )
    )


    conn.commit()

    conn.close()



def show_results():

    conn = sqlite3.connect(
        DB_NAME
    )

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT
        market_id,
        question,
        result

        FROM market_snapshots

        LIMIT 20
        """
    )


    rows = cursor.fetchall()


    for row in rows:

        print(row)


    conn.close()



if __name__ == "__main__":

    show_results()