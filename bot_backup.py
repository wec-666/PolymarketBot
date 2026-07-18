import json

from api_client import get_markets
from scanner import show_top_markets
from portfolio import Portfolio
from trade_engine import TradeEngine
from risk_manager import calculate_position
from database import (
    save_market_snapshot,
    save_account_snapshot
)


# ======================
# 最大持仓数量
# ======================

MAX_POSITIONS = 3


# ======================
# 解析市场价格
# ======================

def parse_market_prices(market):

    raw_prices = market.get(
        "outcomePrices"
    )

    raw_outcomes = market.get(
        "outcomes"
    )

    if not raw_prices:
        return None

    try:

        if isinstance(
            raw_prices,
            str
        ):
            raw_prices = json.loads(
                raw_prices
            )

        if isinstance(
            raw_outcomes,
            str
        ):
            raw_outcomes = json.loads(
                raw_outcomes
            )

        if (
            not isinstance(
                raw_prices,
                list
            )
            or
            len(raw_prices) < 2
        ):
            return None

        prices = [
            float(price)
            for price in raw_prices
        ]

        for price in prices:

            if (
                price < 0
                or
                price > 1
            ):
                return None

        # 优先根据 outcomes 判断 YES 和 NO 顺序
        if (
            isinstance(
                raw_outcomes,
                list
            )
            and
            len(raw_outcomes)
            ==
            len(prices)
        ):

            result = {}

            for outcome, price in zip(
                raw_outcomes,
                prices
            ):

                outcome_name = str(
                    outcome
                ).strip().upper()

                if outcome_name == "YES":

                    result[
                        "YES"
                    ] = price

                elif outcome_name == "NO":

                    result[
                        "NO"
                    ] = price

            if (
                "YES" in result
                and
                "NO" in result
            ):
                return result

        # 兼容标准二元市场
        return {
            "YES": prices[0],
            "NO": prices[1]
        }

    except (
        json.JSONDecodeError,
        TypeError,
        ValueError,
        IndexError
    ):

        return None


# ======================
# 创建全部市场价格表
# ======================

def build_price_map(markets):

    price_map = {}

    for market in markets:

        question = market.get(
            "question"
        )

        if not question:
            continue

        prices = parse_market_prices(
            market
        )

        if prices is None:
            continue

        price_map[
            question
        ] = prices

    return price_map


# ======================
# 显示自动平仓结果
# Telegram 暂时关闭
# ======================

def show_close_results(
    close_results
):

    for result in close_results:

        if not result.get(
            "success"
        ):
            continue

        if result.get(
            "action"
        ) != "CLOSE":
            continue

        reason = result.get(
            "reason",
            "UNKNOWN"
        )

        if reason == "TAKE_PROFIT":

            reason_text = "止盈"

        elif reason == "STOP_LOSS":

            reason_text = "止损"

        else:

            reason_text = reason

        print()
        print("======================")
        print("📢 自动平仓结果")
        print("======================")

        print(
            "市场:",
            result.get(
                "market"
            )
        )

        print(
            "平仓原因:",
            reason_text
        )

        print(
            "平仓价格:",
            result.get(
                "close_price"
            )
        )

        print(
            "盈亏:",
            result.get(
                "profit",
                0
            )
        )

        print(
            "收益率:",
            result.get(
                "profit_percent",
                0
            ),
            "%"
        )


# ======================
# 显示最大持仓提示
# ======================

def show_position_limit(
    account
):

    print()
    print("======================")
    print("📌 当前持仓已达到上限")
    print("======================")

    print(
        "当前持仓:",
        len(
            account.positions
        )
    )

    print(
        "最大允许持仓:",
        MAX_POSITIONS
    )

    print()
    print(
        "本轮停止开新仓，仅监控已有持仓"
    )


# ======================
# 主程序
# ======================

def run_bot():

    print()
    print("======================")
    print("🤖 Polymarket AI Bot启动")
    print("======================")

    # 加载模拟账户
    account = Portfolio(
        100
    )

    # 创建交易引擎
    engine = TradeEngine(
        account,
        take_profit=20,
        stop_loss=-10
    )

    # 获取市场数据
    markets = get_markets()

    if not markets:

        print(
            "❌没有获取到市场数据"
        )

        return

    print()
    print(
        "获取市场数量:",
        len(markets)
    )

    # ======================
    # 先检查已有持仓
    # ======================

    price_map = build_price_map(
        markets
    )

    if account.positions:

        print()
        print("======================")
        print("📊 检查已有持仓")
        print("======================")

        # 将新开仓转换为正常监控状态
        for position in account.positions:
            if getattr(position, "status", None) == "OPEN":
                position.start_monitoring()

        position_results = (
            engine.check_all_positions(
                price_map
            )
        )

        show_close_results(
            position_results
        )

    else:

        print()
        print(
            "当前没有持仓"
        )

    # ======================
    # 检查完旧持仓以后
    # 再判断是否达到持仓上限
    # ======================

    if (
        len(account.positions)
        >=
        MAX_POSITIONS
    ):

        show_position_limit(
            account
        )

        account.report()

        return

    # ======================
    # 扫描重点市场
    # ======================

    results = show_top_markets(
        markets
    )

    if not results:

        print()
        print(
            "⚠️没有发现可分析市场"
        )

        account.report()

        return

    print()
    print("======================")
    print("🤖 自动交易检测")
    print("======================")

    opened_trade = False

    # 每次扫描最多开一笔新仓
    for item in results:

        # 再次检查持仓上限
        # 防止未来循环逻辑修改后超限
        if (
            len(account.positions)
            >=
            MAX_POSITIONS
        ):

            show_position_limit(
                account
            )

            break

        market = item.get(
            "market"
        )

        score = item.get(
            "score",
            0
        )

        signal = item.get(
            "signal",
            "HOLD"
        )

        if not market:
            continue

        question = market.get(
            "question"
        )

        if not question:
            continue

        prices = parse_market_prices(
            market
        )

        if prices:

            try:

                save_market_snapshot(
                    market_id=market.get("id"),
                    question=question,
                    yes_price=prices["YES"],
                    no_price=prices["NO"],
                    volume=float(
                        market.get(
                            "volume",
                            0
                        )
                    ),
                    score=score,
                    signal=signal
                )

            except Exception as error:

                print(
                    "⚠️ 市场快照保存失败:",
                    error
                )

        # 只处理买入信号
        if signal not in [
            "BUY_YES",
            "BUY_NO"
        ]:
            continue
        # 防止重复持仓
        if account.has_position(
            question
        ):

            print()
            print(
                "⚠️ 已有持仓，跳过:"
            )

            print(
                question
            )

            continue

        prices = parse_market_prices(
            market
        )

        if prices is None:

            print()
            print(
                "⚠️价格解析失败，跳过:"
            )

            print(
                question
            )

            continue

        if signal == "BUY_YES":

            price = prices[
                "YES"
            ]

            direction_text = "YES"

        else:

            price = prices[
                "NO"
            ]

            direction_text = "NO"

        try:

            volume = float(
                market.get(
                    "volume",
                    0
                )
            )

        except (
            TypeError,
            ValueError
        ):

            volume = 0

        amount = calculate_position(
            account.balance
        )

        try:

            amount = float(
                amount
            )

        except (
            TypeError,
            ValueError
        ):

            print(
                "⚠️仓位金额格式错误"
            )

            continue

        if amount <= 0:

            print(
                "⚠️计算出的投入金额无效"
            )

            continue

        print()
        print(
            "发现交易机会:"
        )

        print(
            question
        )

        print(
            "信号:",
            signal
        )

        print(
            "方向:",
            direction_text
        )

        print(
            "价格:",
            price
        )

        print(
            "评分:",
            score
        )

        print(
            "交易量:",
            volume
        )

        print(
            "投入:",
            amount
        )

        # 执行模拟交易
        trade_result = engine.execute(
            market=question,
            signal=signal,
            amount=amount,
            price=price
        )

        if trade_result.get(
            "success"
        ):

            print()
            print(
                "📵 Telegram通知目前已关闭"
            )

            print(
                "当前持仓数量:",
                len(
                    account.positions
                ),
                "/",
                MAX_POSITIONS
            )

            opened_trade = True

            # 每轮只允许开一笔新仓
            break

    if not opened_trade:

        print()
        print(
            "本轮没有执行新交易"
        )

    # 输出账户报告
    account.report()
    save_account_snapshot(
        balance=account.balance,
        invested_capital=account.invested_capital(),
        position_count=len(account.positions),
        realized_profit=account.realized_profit()
    )


# ======================
# 程序入口
# ======================

if __name__ == "__main__":

    run_bot()