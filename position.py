import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


VALID_DIRECTIONS = {"BUY_YES", "BUY_NO"}
VALID_STATUSES = {
    "OPEN",
    "MONITORING",
    "TAKE_PROFIT_REVIEW",
    "STOP_LOSS_REVIEW",
    "CLOSED",
}


@dataclass
class Position:
    """
    Polymarket 模拟持仓对象。

    设计目标：
    1. 兼容现有 portfolio.py 使用的字典字段；
    2. 支持保存到 account.json；
    3. 支持从旧版持仓字典恢复；
    4. 统一计算当前价值、浮动盈亏和收益率；
    5. 为 Phase 5 智能动态止盈止损预留状态字段。
    """

    market: str
    direction: str
    amount: float
    price: float
    shares: float
    open_time: float = field(default_factory=time.time)
    status: str = "OPEN"

    # 实时持仓数据
    current_price: Optional[float] = None

    # 可选扩展字段
    market_id: Optional[str] = None
    question: Optional[str] = None
    score: Optional[float] = None
    signal: Optional[str] = None

    # Phase 5 智能止盈止损预留字段
    take_profit_triggered: bool = False
    stop_loss_triggered: bool = False
    last_review_price: Optional[float] = None
    next_profit_review_percent: float = 20.0
    stop_loss_reference_price: Optional[float] = None
    force_stop_price: Optional[float] = None
    ai_rise_probability: Optional[float] = None
    ai_fall_probability: Optional[float] = None

    # 平仓字段
    close_price: Optional[float] = None
    close_value: Optional[float] = None
    profit: Optional[float] = None
    profit_percent: Optional[float] = None
    close_time: Optional[float] = None
    close_reason: Optional[str] = None

    def __post_init__(self) -> None:
        self.market = str(self.market).strip()
        self.direction = str(self.direction).strip().upper()
        self.status = str(self.status).strip().upper()

        self.amount = round(float(self.amount), 4)
        self.price = round(float(self.price), 6)
        self.shares = round(float(self.shares), 6)
        self.open_time = float(self.open_time)

        if self.current_price is not None:
            self.current_price = round(float(self.current_price), 6)

        self._validate()

    def _validate(self) -> None:
        if not self.market:
            raise ValueError("市场名称不能为空")

        if self.direction not in VALID_DIRECTIONS:
            raise ValueError(
                f"无效交易方向: {self.direction}，"
                f"只允许 BUY_YES 或 BUY_NO"
            )

        if self.status not in VALID_STATUSES:
            raise ValueError(
                f"无效持仓状态: {self.status}，"
                f"只允许 OPEN 或 CLOSED"
            )

        if self.amount <= 0:
            raise ValueError("投入金额必须大于0")

        if not 0 < self.price <= 1:
            raise ValueError("开仓价格必须在0到1之间")

        if self.shares <= 0:
            raise ValueError("持仓份额必须大于0")

        if self.current_price is not None:
            self._validate_price(self.current_price, "当前价格")

    @staticmethod
    def _validate_price(price: float, field_name: str = "价格") -> None:
        if not 0 <= price <= 1:
            raise ValueError(f"{field_name}必须在0到1之间")

    @property
    def side(self) -> str:
        return "YES" if self.direction == "BUY_YES" else "NO"

    @property
    def entry_price(self) -> float:
        return self.price

    def update_price(self, current_price: float) -> Dict[str, float]:
        current_price = round(float(current_price), 6)
        self._validate_price(current_price, "当前价格")
        self.current_price = current_price
        return self.profit_details(current_price)

    def current_value(self, current_price: Optional[float] = None) -> float:
        price = self._resolve_price(current_price)
        return round(self.shares * price, 4)

    def unrealized_profit(
        self,
        current_price: Optional[float] = None
    ) -> float:
        value = self.current_value(current_price)
        profit = value - self.amount

        if abs(profit) < 0.005:
            profit = 0.0

        return round(profit, 2)

    def unrealized_profit_percent(
        self,
        current_price: Optional[float] = None
    ) -> float:
        profit = self.unrealized_profit(current_price)

        if self.amount <= 0:
            return 0.0

        result = profit / self.amount * 100

        if abs(result) < 0.005:
            result = 0.0

        return round(result, 2)

    def profit_details(
        self,
        current_price: Optional[float] = None
    ) -> Dict[str, Any]:
        price = self._resolve_price(current_price)

        return {
            "market": self.market,
            "direction": self.direction,
            "side": self.side,
            "entry_price": round(self.price, 6),
            "current_price": round(price, 6),
            "amount": round(self.amount, 2),
            "shares": round(self.shares, 6),
            "current_value": self.current_value(price),
            "profit": self.unrealized_profit(price),
            "profit_percent": self.unrealized_profit_percent(price),
            "status": self.status,
        }

    def start_monitoring(self) -> None:
        """
        开始正常监控持仓
        """
        if self.status == "OPEN":
            self.status = "MONITORING"

    def request_take_profit_review(self) -> None:
        """
        进入止盈AI复审
        """
        if self.status == "MONITORING":
            self.status = "TAKE_PROFIT_REVIEW"

    def request_stop_loss_review(self) -> None:
        """
        进入止损AI复审
        """
        if self.status == "MONITORING":
            self.status = "STOP_LOSS_REVIEW"

    def resume_monitoring(self) -> None:
        """
        AI决定继续持有，恢复正常监控
        """
        if self.status in (
            "TAKE_PROFIT_REVIEW",
            "STOP_LOSS_REVIEW",
        ):
            self.status = "MONITORING"

    def close(
        self,
        close_price: float,
        reason: str = "MANUAL",
        close_time: Optional[float] = None
    ) -> Dict[str, Any]:
        if self.status == "CLOSED":
            raise RuntimeError("该持仓已经平仓")

        close_price = round(float(close_price), 6)
        self._validate_price(close_price, "平仓价格")

        self.current_price = close_price
        self.close_price = close_price
        self.close_value = self.current_value(close_price)
        self.profit = self.unrealized_profit(close_price)
        self.profit_percent = self.unrealized_profit_percent(close_price)
        self.close_time = float(close_time or time.time())
        self.close_reason = str(reason or "MANUAL")
        self.status = "CLOSED"

        return self.to_dict()

    def _resolve_price(
        self,
        current_price: Optional[float]
    ) -> float:
        if current_price is not None:
            price = round(float(current_price), 6)
            self._validate_price(price, "当前价格")
            return price

        if self.current_price is not None:
            return self.current_price

        return self.price

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为兼容旧版 portfolio.py / account.json 的字典。
        """
        data: Dict[str, Any] = {
            "market": self.market,
            "amount": round(self.amount, 4),
            "price": round(self.price, 6),
            "shares": round(self.shares, 6),
            "direction": self.direction,
            "open_time": self.open_time,
            "status": self.status,
        }

        optional_fields = {
            "current_price": self.current_price,
            "market_id": self.market_id,
            "question": self.question,
            "score": self.score,
            "signal": self.signal,
            "take_profit_triggered": self.take_profit_triggered,
            "stop_loss_triggered": self.stop_loss_triggered,
            "last_review_price": self.last_review_price,
            "next_profit_review_percent": self.next_profit_review_percent,
            "stop_loss_reference_price": self.stop_loss_reference_price,
            "force_stop_price": self.force_stop_price,
            "ai_rise_probability": self.ai_rise_probability,
            "ai_fall_probability": self.ai_fall_probability,
            "close_price": self.close_price,
            "close_value": self.close_value,
            "profit": self.profit,
            "profit_percent": self.profit_percent,
            "close_time": self.close_time,
            "close_reason": self.close_reason,
        }

        for key, value in optional_fields.items():
            if value is not None:
                data[key] = value

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Position":
        """
        从旧版或新版持仓字典恢复 Position 对象。
        """
        if not isinstance(data, dict):
            raise TypeError("持仓数据必须是字典")

        market = (
            data.get("market")
            or data.get("question")
            or data.get("market_id")
        )

        if not market:
            raise ValueError("持仓数据缺少 market 字段")

        amount = float(data.get("amount", 0))
        price = float(
            data.get(
                "price",
                data.get("entry_price", 0)
            )
        )

        shares = data.get("shares")
        if shares is None:
            if price <= 0:
                raise ValueError("无法根据持仓数据计算 shares")
            shares = amount / price

        position = cls(
            market=market,
            direction=data.get("direction", ""),
            amount=amount,
            price=price,
            shares=float(shares),
            open_time=float(data.get("open_time", time.time())),
            status=data.get("status", "OPEN"),
            current_price=data.get("current_price"),
            market_id=data.get("market_id"),
            question=data.get("question"),
            score=data.get("score"),
            signal=data.get("signal"),
            take_profit_triggered=bool(
                data.get("take_profit_triggered", False)
            ),
            stop_loss_triggered=bool(
                data.get("stop_loss_triggered", False)
            ),
            last_review_price=data.get("last_review_price"),
            next_profit_review_percent=float(
                data.get("next_profit_review_percent", 20.0)
            ),
            stop_loss_reference_price=data.get(
                "stop_loss_reference_price"
            ),
            force_stop_price=data.get("force_stop_price"),
            ai_rise_probability=data.get("ai_rise_probability"),
            ai_fall_probability=data.get("ai_fall_probability"),
            close_price=data.get("close_price"),
            close_value=data.get("close_value"),
            profit=data.get("profit"),
            profit_percent=data.get("profit_percent"),
            close_time=data.get("close_time"),
            close_reason=data.get("close_reason"),
        )

        return position

    def __getitem__(self, key: str) -> Any:
        """
        提供 position["market"] 形式的兼容访问。
        """
        return self.to_dict()[key]

    def get(self, key: str, default: Any = None) -> Any:
        """
        提供 position.get("market") 形式的兼容访问。
        """
        return self.to_dict().get(key, default)

    def __repr__(self) -> str:
        return (
            "Position("
            f"market={self.market!r}, "
            f"direction={self.direction!r}, "
            f"amount={self.amount}, "
            f"price={self.price}, "
            f"status={self.status!r}"
            ")"
        )
