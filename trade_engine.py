from review_engine import ReviewEngine


class TradeEngine:

    def __init__(
        self,
        account,
        take_profit=20,
        stop_loss=-10,
        review_engine=None
    ):

        self.account = account

        self.take_profit = float(
            take_profit
        )

        self.stop_loss = float(
            stop_loss
        )

        self.review_engine = (
            review_engine
            or ReviewEngine()
        )

    # ======================
    # 执行开仓
    # ======================

    def execute(
        self,
        market,
        signal,
        amount,
        price,
        snapshot_id=None
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
    # 保存账户状态
    # ======================

    def _save_account(self):

        if hasattr(
            self.account,
            "save"
        ):
            self.account.save()

    # ======================
    # 检查单个持仓
    # ======================

    def check_position(
        self,
        market,
        current_price,
        market_score=None
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

        # ======================
        # Phase 5.2B：AI止盈复审
        # ======================

        if (
            profit_percent
            >=
            self.take_profit
        ):

            position = self.account.get_position(
                market
            )

            if position is None:

                return {
                    "success": False,
                    "action": "NO_POSITION",
                    "market": market
                }

            if hasattr(
                position,
                "request_take_profit_review"
            ):
                position.request_take_profit_review()

            self._save_account()

            print(
                "🤖进入AI止盈复审"
            )

            # 优先使用外部传入评分，
            # 其次读取持仓自身保存的评分。
            if market_score is None:
                market_score = position.get(
                    "score"
                )

            # 缺少评分时不允许自动平仓，
            # 防止旧持仓因 score=None 被当成0分。
            if market_score is None:

                if hasattr(
                    position,
                    "resume_monitoring"
                ):
                    position.resume_monitoring()

                self._save_account()

                print(
                    "⚠️缺少市场评分，本轮暂不执行AI平仓"
                )

                print(
                    "⏳恢复持仓监控"
                )

                return {
                    "success": True,
                    "action": "HOLD",
                    "market": market,
                    "reason": "MISSING_MARKET_SCORE",
                    "profit": profit,
                    "profit_percent": profit_percent,
                    "current_price": current_price
                }

            # ReviewEngine 需要包含最新盈亏的数据。
            review_position = dict(
                position.to_dict()
                if hasattr(position, "to_dict")
                else position
            )

            review_position.update(
                {
                    "profit": profit,
                    "profit_percent": profit_percent,
                    "current_price": current_price
                }
            )

            decision = (
                self.review_engine
                .review_take_profit(
                    position=review_position,
                    market_score=market_score
                )
            )

            action = str(
                decision.get(
                    "action",
                    "HOLD"
                )
            ).upper()

            reason = decision.get(
                "reason",
                "未提供原因"
            )

            confidence = decision.get(
                "confidence",
                0
            )

            print(
                "AI决策:",
                action
            )

            print(
                "决策原因:",
                reason
            )

            print(
                "置信度:",
                confidence
            )

            if action == "CLOSE":

                close_result = self.settle(
                    market=market,
                    close_price=current_price,
                    reason="AI_TAKE_PROFIT"
                )

                close_result[
                    "profit"
                ] = profit

                close_result[
                    "profit_percent"
                ] = profit_percent

                close_result[
                    "review"
                ] = decision

                return close_result

            if hasattr(
                position,
                "resume_monitoring"
            ):
                position.resume_monitoring()

            self._save_account()

            print(
                "⏳AI决定继续持有"
            )

            return {
                "success": True,
                "action": "HOLD",
                "market": market,
                "direction": result["direction"],
                "profit": profit,
                "profit_percent": profit_percent,
                "current_price": current_price,
                "review": decision
            }

        # ======================
        # Phase 5.3A：AI止损复审
        # ======================
        if (
            profit_percent
            <=
            self.stop_loss
        ):

            position = self.account.get_position(
                market
            )

            if position is None:
                return {
                    "success": False,
                    "action": "NO_POSITION",
                    "market": market
                }

            if hasattr(position,"request_stop_loss_review"):
                position.request_stop_loss_review()

            self._save_account()

            print("🤖进入AI止损复审")

            if market_score is None:
                market_score = position.get("score")

            if market_score is None:

                if hasattr(position,"resume_monitoring"):
                    position.resume_monitoring()

                self._save_account()

                print("⚠️缺少市场评分，本轮暂不执行AI止损")
                print("⏳恢复持仓监控")

                return {
                    "success": True,
                    "action": "HOLD",
                    "market": market,
                    "reason": "MISSING_MARKET_SCORE",
                    "profit": profit,
                    "profit_percent": profit_percent,
                    "current_price": current_price
                }

            review_position = dict(
                position.to_dict()
                if hasattr(position,"to_dict")
                else position
            )

            review_position.update({
                "profit": profit,
                "profit_percent": profit_percent,
                "current_price": current_price
            })

            decision = self.review_engine.review_stop_loss(
                position=review_position,
                market_score=market_score
            )

            action = str(decision.get("action","HOLD")).upper()

            print("AI决策:", action)
            print("决策原因:", decision.get("reason",""))
            print("置信度:", decision.get("confidence",0))

            if action == "CLOSE":

                close_result = self.settle(
                    market=market,
                    close_price=current_price,
                    reason="AI_STOP_LOSS"
                )

                close_result["profit"] = profit
                close_result["profit_percent"] = profit_percent
                close_result["review"] = decision

                return close_result

            if hasattr(position,"resume_monitoring"):
                position.resume_monitoring()

            self._save_account()

            print("⏳AI决定继续持有")

            return {
                "success": True,
                "action": "HOLD",
                "market": market,
                "direction": result["direction"],
                "profit": profit,
                "profit_percent": profit_percent,
                "current_price": current_price,
                "review": decision
            }

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
        price_map,
        score_map=None
    ):

        results = []

        score_map = score_map or {}

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
                current_price=current_price,
                market_score=score_map.get(
                    market
                )
            )

            results.append(
                result
            )

        return results
