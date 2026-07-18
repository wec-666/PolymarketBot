import json
import os
import time
from copy import deepcopy

from database import (
    save_open_trade,
    close_trade_record
)

from position import Position


class Portfolio:

    def __init__(self, capital):

        self.file = "account.json"

        if capital <= 0:
            raise ValueError(
                "初始资金必须大于0"
            )

        if os.path.exists(
            self.file
        ):

            self.load()

        else:

            self.initial_capital = round(
                float(capital),
                2
            )

            self.balance = round(
                float(capital),
                2
            )

            # 可用余额（保留 balance 兼容旧代码）
            self.available_balance = self.balance

            # 当前持仓投入资金
            self.invested_balance = 0.0

            # 账户净值（当前阶段按账面投入计算）
            self.equity = self.balance

            # 账户总资产
            self.total_assets = self.balance

            self.positions = []
            self.history = []

            self.refresh_account()
            self.save()

    # ======================
    # 保存账户
    # ======================

    def save(self):

        # 保存前统一刷新账户派生数据
        self.refresh_account()

        data = {
            "initial_capital": self.initial_capital,
            "balance": self.balance,
            "available_balance": self.available_balance,
            "invested_balance": self.invested_balance,
            "equity": self.equity,
            "total_assets": self.total_assets,
            "positions": [
                position.to_dict()
                if isinstance(position, Position)
                else position
                for position in self.positions
            ],
            "history": self.history
        }

        temp_file = (
            self.file
            +
            ".tmp"
        )

        try:

            with open(
                temp_file,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=4
                )

            os.replace(
                temp_file,
                self.file
            )

        except Exception as error:

            print(
                "❌账户保存失败:",
                error
            )

            if os.path.exists(
                temp_file
            ):

                os.remove(
                    temp_file
                )

            raise

    # ======================
    # 加载账户
    # ======================

    def load(self):

        try:

            with open(
                self.file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(
                    file
                )

            self.initial_capital = float(
                data.get(
                    "initial_capital",
                    0
                )
            )

            self.balance = float(
                data.get(
                    "balance",
                    self.initial_capital
                )
            )

            # 兼容旧版 account.json：缺少新字段时自动计算
            self.available_balance = float(
                data.get(
                    "available_balance",
                    self.balance
                )
            )

            self.invested_balance = float(
                data.get(
                    "invested_balance",
                    0
                )
            )

            self.equity = float(
                data.get(
                    "equity",
                    self.available_balance
                    +
                    self.invested_balance
                )
            )

            self.total_assets = float(
                data.get(
                    "total_assets",
                    self.equity
                )
            )

            raw_positions = data.get(
                "positions",
                []
            )

            self.positions = []

            if isinstance(raw_positions, list):

                for item in raw_positions:

                    try:

                        if isinstance(item, Position):

                            self.positions.append(
                                item
                            )

                        elif isinstance(item, dict):

                            self.positions.append(
                                Position.from_dict(
                                    item
                                )
                            )

                    except (
                        TypeError,
                        ValueError
                    ) as error:

                        print(
                            "⚠️跳过无效持仓数据:",
                            error
                        )

            self.history = data.get(
                "history",
                []
            )

            if self.initial_capital <= 0:

                raise ValueError(
                    "账户初始资金数据无效"
                )

            if not isinstance(
                self.positions,
                list
            ):

                self.positions = []

            if not isinstance(
                self.history,
                list
            ):

                self.history = []

            # 使用实际余额和持仓重新同步账户数据
            self.refresh_account()

        except (
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError
        ) as error:

            raise RuntimeError(
                f"account.json加载失败，请检查账户文件：{error}"
            ) from error

    # ======================
    # 刷新账户状态
    # ======================

    def refresh_account(
        self,
        current_prices=None
    ):

        """
        统一刷新账户派生字段。

        current_prices 可传入：
        {"市场名称": 当前价格}

        未传入当前价格时，净值按持仓成本计算；
        传入后，净值按最新市场价格计算。
        """

        self.balance = round(
            float(self.balance),
            4
        )

        self.available_balance = self.balance

        invested = 0.0
        position_value = 0.0

        for position in self.positions:

            if position.get(
                "status",
                "OPEN"
            ) != "OPEN":

                continue

            amount = float(
                position.get(
                    "amount",
                    0
                )
            )

            shares = float(
                position.get(
                    "shares",
                    0
                )
            )

            entry_price = float(
                position.get(
                    "price",
                    0
                )
            )

            invested += amount

            market = position.get(
                "market"
            )

            current_price = entry_price

            if isinstance(
                current_prices,
                dict
            ):

                candidate = current_prices.get(
                    market
                )

                try:

                    candidate = float(
                        candidate
                    )

                    if 0 <= candidate <= 1:

                        current_price = candidate

                except (
                    TypeError,
                    ValueError
                ):

                    pass

            position_value += (
                shares
                *
                current_price
            )

        self.invested_balance = round(
            invested,
            4
        )

        self.equity = round(
            self.available_balance
            +
            position_value,
            4
        )

        self.total_assets = self.equity

        return {
            "available_balance": self.available_balance,
            "invested_balance": self.invested_balance,
            "equity": self.equity,
            "total_assets": self.total_assets
        }

    # ======================
    # 获取指定持仓
    # ======================

    def get_position(
        self,
        market
    ):

        for position in self.positions:

            if (
                position.get(
                    "market"
                )
                ==
                market
                and
                position.get(
                    "status",
                    "OPEN"
                )
                ==
                "OPEN"
            ):

                return position

        return None

    # ======================
    # 查询是否已有持仓
    # ======================

    def has_position(
        self,
        market
    ):

        return (
            self.get_position(
                market
            )
            is not None
        )

    # ======================
    # 开仓
    # ======================

    def open_trade(
        self,
        market,
        amount,
        direction,
        price
    ):

        try:

            amount = float(
                amount
            )

            price = float(
                price
            )

        except (
            TypeError,
            ValueError
        ):

            print(
                "❌开仓金额或价格格式错误"
            )

            return False

        if not market:

            print(
                "❌市场名称不能为空"
            )

            return False

        if direction not in [
            "BUY_YES",
            "BUY_NO"
        ]:

            print(
                "❌交易方向无效:",
                direction
            )

            return False

        if amount <= 0:

            print(
                "❌投入金额必须大于0"
            )

            return False

        if (
            price <= 0
            or
            price > 1
        ):

            print(
                "❌交易价格必须在0到1之间"
            )

            return False

        if amount > self.balance:

            print(
                "❌余额不足"
            )

            print(
                "当前余额:",
                round(
                    self.balance,
                    2
                )
            )

            print(
                "需要资金:",
                round(
                    amount,
                    2
                )
            )

            return False

        if self.has_position(
            market
        ):

            print(
                "⚠️已有该市场持仓，跳过重复开仓"
            )

            return False

        risk_ratio = (
            amount
            /
            self.initial_capital
        )

        if risk_ratio > 0.05:

            print(
                "⚠️超过单笔5%资金限制"
            )

            print(
                "最大允许投入:",
                round(
                    self.initial_capital
                    *
                    0.05,
                    2
                )
            )

            return False

        shares = (
            amount
            /
            price
        )

        open_time = time.time()

        try:

            trade = Position(
                market=market,
                amount=amount,
                price=price,
                shares=shares,
                direction=direction,
                open_time=open_time,
                status="OPEN"
            )

        except (
            TypeError,
            ValueError
        ) as error:

            print(
                "❌创建持仓对象失败:",
                error
            )

            return False

        self.balance = round(
            self.balance
            -
            amount,
            4
        )

        self.positions.append(
            trade
        )

        self.refresh_account()
        self.save()

        try:

            save_open_trade(
                market=market,
                direction=direction,
                amount=amount,
                open_price=price,
                shares=shares,
                open_time=open_time
            )

        except Exception as error:

            print()
            print(
                "⚠️数据库开仓记录保存失败:"
            )

            print(
                error
            )

        print()
        print(
            "🚀 开仓成功"
        )

        print(
            "市场:",
            market
        )

        print(
            "方向:",
            direction
        )

        print(
            "价格:",
            round(
                price,
                4
            )
        )

        print(
            "份额:",
            round(
                shares,
                2
            )
        )

        print(
            "投入:",
            round(
                amount,
                2
            )
        )

        print(
            "剩余余额:",
            round(
                self.balance,
                2
            )
        )

        return True

    # ======================
    # 计算持仓盈亏详情
    # ======================

    def position_profit(
        self,
        market,
        current_price
    ):

        position = self.get_position(
            market
        )

        if position is None:

            return None

        if isinstance(
            position,
            Position
        ):

            try:

                return position.profit_details(
                    current_price
                )

            except (
                TypeError,
                ValueError
            ):

                return None

        try:

            current_price = float(
                current_price
            )

        except (
            TypeError,
            ValueError
        ):

            return None

        if (
            current_price < 0
            or
            current_price > 1
        ):

            return None

        current_value = (
            position[
                "shares"
            ]
            *
            current_price
        )

        profit = (
            current_value
            -
            position[
                "amount"
            ]
        )

        if position[
            "amount"
        ] > 0:

            profit_percent = (
                profit
                /
                position[
                    "amount"
                ]
                *
                100
            )

        else:

            profit_percent = 0

        if abs(
            profit
        ) < 0.005:

            profit = 0.0

        if abs(
            profit_percent
        ) < 0.005:

            profit_percent = 0.0

        return {
            "market": market,
            "direction": position[
                "direction"
            ],
            "entry_price": round(
                position[
                    "price"
                ],
                6
            ),
            "current_price": round(
                current_price,
                6
            ),
            "amount": round(
                position[
                    "amount"
                ],
                2
            ),
            "shares": round(
                position[
                    "shares"
                ],
                6
            ),
            "current_value": round(
                current_value,
                2
            ),
            "profit": round(
                profit,
                2
            ),
            "profit_percent": round(
                profit_percent,
                2
            )
        }

    # ======================
    # 浮动盈亏金额
    # ======================

    def unrealized_profit(
        self,
        market,
        current_price
    ):

        result = self.position_profit(
            market,
            current_price
        )

        if result is None:

            return None

        return result[
            "profit"
        ]

    # ======================
    # 浮动盈亏百分比
    # ======================

    def unrealized_profit_percent(
        self,
        market,
        current_price
    ):

        result = self.position_profit(
            market,
            current_price
        )

        if result is None:

            return None

        return result[
            "profit_percent"
        ]

    # ======================
    # 平仓
    # ======================

    def close_trade(
        self,
        market,
        close_price,
        reason="MANUAL"
    ):

        target = self.get_position(
            market
        )

        if target is None:

            print(
                "❌没有找到持仓"
            )

            return False

        try:

            close_price = float(
                close_price
            )

        except (
            TypeError,
            ValueError
        ):

            print(
                "❌平仓价格格式错误"
            )

            return False

        if (
            close_price < 0
            or
            close_price > 1
        ):

            print(
                "❌平仓价格必须在0到1之间"
            )

            return False

        if isinstance(
            target,
            Position
        ):

            try:

                closed_trade = target.close(
                    close_price=close_price,
                    reason=reason
                )

            except (
                TypeError,
                ValueError,
                RuntimeError
            ) as error:

                print(
                    "❌平仓失败:",
                    error
                )

                return False

            value = float(
                closed_trade.get(
                    "close_value",
                    0
                )
            )

            profit = float(
                closed_trade.get(
                    "profit",
                    0
                )
            )

            profit_percent = float(
                closed_trade.get(
                    "profit_percent",
                    0
                )
            )

        else:

            value = (
                target[
                    "shares"
                ]
                *
                close_price
            )

            profit = (
                value
                -
                target[
                    "amount"
                ]
            )

            if target[
                "amount"
            ] > 0:

                profit_percent = (
                    profit
                    /
                    target[
                        "amount"
                    ]
                    *
                    100
                )

            else:

                profit_percent = 0

            if abs(
                profit
            ) < 0.005:

                profit = 0.0

            if abs(
                profit_percent
            ) < 0.005:

                profit_percent = 0.0

            closed_trade = deepcopy(
                target
            )

            closed_trade[
                "close_price"
            ] = round(
                close_price,
                6
            )

            closed_trade[
                "close_value"
            ] = round(
                value,
                4
            )

            closed_trade[
                "profit"
            ] = round(
                profit,
                2
            )

            closed_trade[
                "profit_percent"
            ] = round(
                profit_percent,
                2
            )

            closed_trade[
                "close_time"
            ] = time.time()

            closed_trade[
                "close_reason"
            ] = reason

            closed_trade[
                "status"
            ] = "CLOSED"

        self.balance = round(
            self.balance
            +
            value,
            4
        )

        self.history.append(
            closed_trade
        )

        self.positions.remove(
            target
        )

        self.refresh_account()
        self.save()

        try:

            close_trade_record(
                market=market,
                direction=target["direction"],
                close_price=close_price,
                close_time=closed_trade["close_time"],
                profit=closed_trade["profit"],
                profit_percent=closed_trade["profit_percent"],
                close_reason=reason
            )

        except Exception as error:

            print()
            print(
                "⚠️数据库平仓记录更新失败:"
            )

            print(
                error
            )

        print()
        print(
            "✅ 平仓完成"
        )

        print(
            "市场:",
            market
        )

        print(
            "方向:",
            target[
                "direction"
            ]
        )

        print(
            "开仓价格:",
            target[
                "price"
            ]
        )

        print(
            "平仓价格:",
            round(
                close_price,
                4
            )
        )

        print(
            "平仓原因:",
            reason
        )

        print(
            "收益:",
            round(
                profit,
                2
            )
        )

        print(
            "收益率:",
            round(
                profit_percent,
                2
            ),
            "%"
        )

        print(
            "当前余额:",
            round(
                self.balance,
                2
            )
        )

        return True

    # ======================
    # 已实现总盈亏
    # ======================

    def realized_profit(self):

        total = 0

        for trade in self.history:

            total += float(
                trade.get(
                    "profit",
                    0
                )
            )

        return round(
            total,
            2
        )

    # ======================
    # 当前持仓投入金额
    # ======================

    def invested_capital(self):

        total = 0

        for position in self.positions:

            total += float(
                position.get(
                    "amount",
                    0
                )
            )

        return round(
            total,
            2
        )

    # ======================
    # 账户报告
    # ======================

    def report(self):

        self.refresh_account()

        realized = self.realized_profit()

        total_trades = len(
            self.history
        )

        win_count = 0
        loss_count = 0

        for trade in self.history:

            profit = float(
                trade.get(
                    "profit",
                    0
                )
            )

            if profit > 0:

                win_count += 1

            elif profit < 0:

                loss_count += 1

        if total_trades > 0:

            win_rate = (
                win_count
                /
                total_trades
                *
                100
            )

        else:

            win_rate = 0

        print()
        print(
            "===================="
        )

        print(
            "🔥 账户报告"
        )

        print(
            "===================="
        )

        print(
            "初始资金:",
            round(
                self.initial_capital,
                2
            )
        )

        print(
            "可用余额:",
            round(
                self.available_balance,
                2
            )
        )

        print(
            "持仓投入:",
            round(
                self.invested_balance,
                2
            )
        )

        print(
            "账户净值:",
            round(
                self.equity,
                2
            )
        )

        print(
            "总资产:",
            round(
                self.total_assets,
                2
            )
        )

        print(
            "当前持仓:",
            len(
                self.positions
            )
        )

        print(
            "历史交易:",
            total_trades
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
            "已实现盈亏:",
            realized
        )

        print(
            "胜率:",
            round(
                win_rate,
                2
            ),
            "%"
        )

        if self.positions:

            print()
            print(
                "📌 当前持仓"
            )

            print(
                "--------------------"
            )

            for position in self.positions:

                print(
                    "市场:",
                    position.get(
                        "market"
                    )
                )

                print(
                    "方向:",
                    position.get(
                        "direction"
                    )
                )

                print(
                    "投入:",
                    round(
                        position.get(
                            "amount",
                            0
                        ),
                        2
                    )
                )

                print(
                    "买入价格:",
                    position.get(
                        "price"
                    )
                )

                print(
                    "份额:",
                    round(
                        position.get(
                            "shares",
                            0
                        ),
                        2
                    )
                )

                print(
                    "--------------------"
                )

        if self.history:

            print()
            print(
                "📚 最近交易"
            )

            print(
                "--------------------"
            )

            for trade in self.history[
                -5:
            ]:

                print(
                    "市场:",
                    trade.get(
                        "market"
                    )
                )

                print(
                    "方向:",
                    trade.get(
                        "direction"
                    )
                )

                print(
                    "盈亏:",
                    trade.get(
                        "profit",
                        0
                    )
                )

                print(
                    "收益率:",
                    trade.get(
                        "profit_percent",
                        0
                    ),
                    "%"
                )

                print(
                    "平仓原因:",
                    trade.get(
                        "close_reason",
                        "UNKNOWN"
                    )
                )

                print(
                    "--------------------"
                )

        print(
            "===================="
        )