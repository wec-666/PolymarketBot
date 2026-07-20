from database import get_connection
class ReviewEngine:
    def get_trade_history(self):

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM trades
            ORDER BY id DESC
            """
        )

        trades = cursor.fetchall()

        connection.close()

        return [dict(trade) for trade in trades]

    def review_take_profit(
        self,
        position,
        market_score
    ):

        """
        AI止盈复审占位逻辑

        返回:
        HOLD  = 继续持有
        CLOSE = 平仓
        """

        score = float(
            market_score or 0
        )

        profit_percent = float(
            position.get(
                "profit_percent",
                0
            )
        )

        if profit_percent >= 50:

            return {
                "action": "CLOSE",
                "reason": "利润已达到50%，优先锁定收益",
                "confidence": 0.95
            }

        if score >= 80:

            return {
                "action": "HOLD",
                "reason": "市场评分较高，趋势仍然较强",
                "confidence": 0.85
            }

        return {
            "action": "CLOSE",
            "reason": "市场评分偏低，建议止盈平仓",
            "confidence": 0.80
        }


    def review_stop_loss(
        self,
        position,
        market_score
    ):

        """
        AI止损复审占位逻辑

        返回:
        HOLD  = 继续持有
        CLOSE = 平仓
        """

        score = float(
            market_score or 0
        )

        profit_percent = float(
            position.get(
                "profit_percent",
                0
            )
        )

        if profit_percent <= -20:

            return {
                "action": "CLOSE",
                "reason": "亏损达到强制风险线",
                "confidence": 0.98
            }

        if score >= 85:

            return {
                "action": "HOLD",
                "reason": "市场评分仍然较高，可能只是正常回撤",
                "confidence": 0.75
            }

        return {
            "action": "CLOSE",
            "reason": "市场评分不足，风险继续扩大",
            "confidence": 0.85
        }
def review_trade(trade):

    print()
    print("====================")
    print("🤖 AI交易复盘")
    print("====================")

    market = trade.get(
        "market"
    )

    direction = trade.get(
        "direction"
    )

    amount = float(
        trade.get(
            "amount",
            0
        )
    )

    open_price = float(
        trade.get(
            "open_price",
            0
        )
    )

    status = trade.get(
        "status"
    )


    score = 50


    if amount <= 5:
        score += 20

    if open_price < 0.6:
        score += 20


    if status == "OPEN":
        advice = "继续观察"

    else:
        advice = "分析已完成"


    print("市场:", market)
    print("方向:", direction)
    print("投入:", amount)
    print("入场价格:", open_price)
    print("状态:", status)

    print()
    print("📊 交易评分:", score, "/100")
    print("🤖 AI建议:", advice)