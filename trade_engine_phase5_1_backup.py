class TradeEngine:

    def __init__(
        self,
        account,
        take_profit=20,
        stop_loss=-10
    ):

        self.account = account

        self.take_profit = float(
            take_profit
        )

        self.stop_loss = float(
            stop_loss
        )

    # ======================
    # 执行开仓
    # ======================

    def execute(
        self,
        market,
        signal,
        amount,
        price
    ):

        print()
        print("======================")
        print("🚀 模拟交易执行")
        print("======================")

        print(
            "市场:",
            market
        )

        print(
            "方向:",
            signal
        )

        print(
            "价格:",
            price
        )

        print(
            "投入:",
            amount
        )

        if signal not in [
            "BUY_YES",
            "BUY_NO"
        ]:

            print(
                "⚠️当前信号不执行交易:",
                signal
            )

            return {
                "success": False,
                "action": "SKIP",
                "reason": "INVALID_SIGNAL"
            }

        success = self.account.open_trade(
            market=market,
            amount=amount,
            direction=signal,
            price=price
        )

        if success:

            print(
                "✅订单执行成功"
            )

            return {
                "success": True,
                "action": "OPEN",
                "market": market,
                "direction": signal,
                "amount": amount,
                "price": price
            }

        print(
            "❌订单执行失败"
        )

        return {
            "success": False,
            "action": "OPEN_FAILED",
            "market": market,
            "direction": signal
        }

    # ======================
    # 手动平仓
    # ======================

    def settle(
        self,
        market,
        close_price,
        reason="MANUAL"
    ):

        success = self.account.close_trade(
            market=market,
            close_price=close_price,
            reason=reason
        )

        if success:

            print()
            print(
                "✅交易结算完成"
            )

            return {
                "success": True,
                "action": "CLOSE",
                "market": market,
                "close_price": close_price,
                "reason": reason
            }

        print()
        print(
            "❌交易结算失败"
        )

        return {
            "success": False,
            "action": "CLOSE_FAILED",
            "market": market
        }

    # ======================
    # 检查单个持仓
    # ======================

    def check_position(
        self,
        market,
        current_price
    ):

        result = self.account.position_profit(
            market=market,
            current_price=current_price
        )

        if result is None:

            return {
                "success": False,
                "action": "NO_POSITION",
                "market": market
            }

        profit = result["profit"]

        profit_percent = result[
            "profit_percent"
        ]

        print()
        print("======================")
        print("📊 持仓检查")
        print("======================")

        print(
            "市场:",
            market
        )

        print(
            "方向:",
            result["direction"]
        )

        print(
            "开仓价格:",
            result["entry_price"]
        )

        print(
            "当前价格:",
            result["current_price"]
        )

        print(
            "浮动盈亏:",
            profit
        )

        print(
            "收益率:",
            profit_percent,
            "%"
        )

        # Phase 5.1：进入AI止盈复审（暂不平仓）
        if (
            profit_percent
            >=
            self.take_profit
        ):

            position = self.account.get_position(
                market
            )

            if (
                position
                and hasattr(
                    position,
                    "request_take_profit_review"
                )
            ):

                position.request_take_profit_review()

                if hasattr(
                    self.account,
                    "save"
                ):
                    self.account.save()

            print(
                "🤖进入AI止盈复审"
            )

            print(
                "等待AI决策..."
            )

            return {
                "success": True,
                "action": "TAKE_PROFIT_REVIEW",
                "market": market,
                "profit": profit,
                "profit_percent": profit_percent,
                "current_price": current_price
            }

        # 止损
        if (
            profit_percent
            <=
            self.stop_loss
        ):

            print(
                "🛑达到止损条件"
            )

            close_result = self.settle(
                market=market,
                close_price=current_price,
                reason="STOP_LOSS"
            )

            close_result[
                "profit"
            ] = profit

            close_result[
                "profit_percent"
            ] = profit_percent

            return close_result

        print(
            "⏳继续持有"
        )

        return {
            "success": True,
            "action": "HOLD",
            "market": market,
            "direction": result["direction"],
            "profit": profit,
            "profit_percent": profit_percent,
            "current_price": current_price
        }

    # ======================
    # 检查全部持仓
    # ======================

    def check_all_positions(
        self,
        price_map
    ):

        results = []

        # 使用副本，避免平仓时修改原列表导致循环异常
        positions = list(
            self.account.positions
        )

        for position in positions:

            market = position.get(
                "market"
            )

            direction = position.get(
                "direction"
            )

            if market not in price_map:

                print()
                print(
                    "⚠️没有找到当前市场价格:",
                    market
                )

                continue

            market_prices = price_map[
                market
            ]

            if isinstance(
                market_prices,
                dict
            ):

                if direction == "BUY_YES":

                    current_price = market_prices.get(
                        "YES"
                    )

                elif direction == "BUY_NO":

                    current_price = market_prices.get(
                        "NO"
                    )

                else:

                    print(
                        "❌未知持仓方向:",
                        direction
                    )

                    continue

            else:

                # 兼容只传一个价格的情况
                current_price = market_prices

            if current_price is None:

                print(
                    "⚠️无法获取持仓当前价格:",
                    market
                )

                continue

            result = self.check_position(
                market=market,
                current_price=current_price
            )

            results.append(
                result
            )

        return results