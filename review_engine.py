class ReviewEngine:

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