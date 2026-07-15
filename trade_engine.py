class TradeEngine:


    def __init__(self, account):

        self.account = account



    def execute(
        self,
        market,
        signal,
        amount
    ):


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
            "投入:",
            amount
        )


        self.account.open_trade(
            market,
            amount,
            signal
        )



    def settle(
        self,
        result,
        profit
    ):


        self.account.close_trade(
            result,
            profit
        )


        print()
        print("交易结算完成")