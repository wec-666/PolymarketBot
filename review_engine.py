from database import get_connection
import json
import os
def get_account_balance():

    try:

        with open(
            "account.json",
            "r",
            encoding="utf-8"
        ) as file:

            account = json.load(file)


        return float(
            account.get(
                "total_assets",
                0
            )
        )


    except Exception:

        return 0
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
    import time


    open_time = float(
        trade.get(
            "open_time",
            0
        ) or 0
    )


    close_time = trade.get(
        "close_time"
    )


    if close_time:

        close_time = float(
            close_time
        )

    else:

        close_time = time.time()



    holding_seconds = (
        close_time - open_time
    )


    holding_hours = (
        holding_seconds / 3600
    )
    profit = float(
        trade.get(
            "profit",
            0
        ) or 0
    )


    profit_percent = float(
        trade.get(
            "profit_percent",
            0
        ) or 0
    )
    account_balance = get_account_balance()


    if account_balance > 0:

        account_risk = (
            amount / account_balance
        ) * 100

    else:

        account_risk = 0


    if account_risk <= 5:

        risk_level = "低风险"

        risk_reason = (
            "仓位占比控制在5%以内"
        )


    elif account_risk <= 10:

        risk_level = "中等风险"

        risk_reason = (
            "仓位占比超过5%，需要关注"
        )


    else:

        risk_level = "高风险"

        risk_reason = (
            "仓位过大，可能影响账户稳定"
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
    print(
        "持仓时间:",
        round(
            holding_hours,
            2
        ),
        "小时"
    )
    print(
        "盈亏:",
        profit
    )


    print(
        "收益率:",
        profit_percent,
        "%"
    )
    print()

    print(
    "账户资产:",
    round(
        account_balance,
        2
    )
    )
    print(
        "🛡️ 风险评价:",
        risk_level
    )
    print()


    if profit_percent > 20 and account_risk <= 5:

        feedback = (
            "成功因素: "
            "收益达到目标，"
            "仓位控制良好，"
            "风险收益比较优秀"
        )


        suggestion = (
            "继续寻找低风险高概率机会"
        )


    elif profit_percent < -10:

        feedback = (
            "失败因素: "
            "亏损超过预期，"
            "需要检查入场逻辑"
        )


        suggestion = (
            "降低仓位，提高信号过滤"
        )


    else:

        feedback = (
            "交易表现正常，"
            "继续观察数据"
        )


        suggestion = (
            "保持当前策略"
        )


    print(
        "🧠 策略反馈:",
    )


    print(
        feedback
    )


    print(
        "优化建议:",
        suggestion
    )


    print(
        "原因:",
        risk_reason
    )
    print()


    if profit_percent >= 20:

        result = "优秀盈利交易"

        result_reason = (
            "收益率达到20%以上，"
            "交易结果良好"
        )


    elif profit_percent > 0:

        result = "小幅盈利交易"

        result_reason = (
            "交易盈利，但收益空间有限"
        )


    elif profit_percent <= -10:

        result = "风险交易"

        result_reason = (
            "亏损超过10%，需要检查策略"
        )


    else:

        result = "正常波动"

        result_reason = (
            "当前结果处于可接受范围"
        )


    print(
        "📈 结果评价:",
        result
    )


    print(
        "原因:",
        result_reason
    )

    print()
    print("📊 交易评分:", score, "/100")
    print("🤖 AI建议:", advice)
def generate_review_report(trade):

    report = {}

    report["market"] = trade.get(
        "market"
    )

    report["direction"] = trade.get(
        "direction"
    )

    report["amount"] = float(
        trade.get(
            "amount",
            0
        )
    )

    report["status"] = trade.get(
        "status"
    )

    report["profit"] = float(
        trade.get(
            "profit",
            0
        ) or 0
    )

    report["profit_percent"] = float(
        trade.get(
            "profit_percent",
            0
        ) or 0
    )


    if report["profit_percent"] >= 20:

        report["result"] = "优秀盈利交易"


    elif report["profit_percent"] > 0:

        report["result"] = "小幅盈利交易"


    elif report["profit_percent"] <= -10:

        report["result"] = "风险交易"


    else:

        report["result"] = "正常波动"


    return report
def generate_full_review_report(trade):


    basic = generate_review_report(
        trade
    )


    profit_percent = basic[
        "profit_percent"
    ]


    amount = basic[
        "amount"
    ]


    account_balance = get_account_balance()


    if account_balance > 0:

        risk_percent = (
            amount /
            account_balance
        ) * 100


    else:

        risk_percent = 0



    if risk_percent <= 5:

        risk_level = "低风险"

        risk_reason = (
            "仓位占比控制在5%以内"
        )


    elif risk_percent <= 10:

        risk_level = "中等风险"

        risk_reason = (
            "仓位较高，需要关注"
        )


    else:

        risk_level = "高风险"

        risk_reason = (
            "仓位过大，影响账户稳定"
        )



    if profit_percent >= 20:

        feedback = (
            "收益达到目标，"
            "仓位控制良好"
        )

        suggestion = (
            "继续寻找低风险高概率机会"
        )


    elif profit_percent < -10:

        feedback = (
            "亏损较大，需要检查策略"
        )

        suggestion = (
            "降低仓位，提高过滤条件"
        )


    else:

        feedback = (
            "交易表现正常"
        )

        suggestion = (
            "继续观察市场数据"
        )



    report = {


        "market":
        basic["market"],


        "direction":
        basic["direction"],


        "trade":
        {


            "amount":
            basic["amount"],


            "profit":
            basic["profit"],


            "profit_percent":
            basic["profit_percent"],


            "status":
            basic["status"]

        },


        "risk":
        {


            "level":
            risk_level,


            "reason":
            risk_reason

        },


        "evaluation":
        {


            "result":
            basic["result"],


            "score":
            90

        },


        "feedback":
        {


            "success":
            feedback,


            "suggestion":
            suggestion

        }


    }


    return report