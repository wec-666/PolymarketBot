class Portfolio:


    def __init__(
        self,
        capital
    ):

        self.initial_capital = capital

        self.balance = capital

        self.trades = []



    def open_trade(
        self,
        market,
        amount,
        direction
    ):

        trade = {

            "market": market,

            "amount": amount,

            "direction": direction

        }


        self.trades.append(
            trade
        )



    def close_trade(
        self,
        result,
        profit
    ):

        self.balance += profit


        self.trades.append({

            "result": result,

            "profit": profit,

            "balance": self.balance

        })



    def report(self):

        print("======================")

        print("🔥 资金报告")

        print("======================")


        print(
            "初始资金:",
            self.initial_capital
        )


        print(
            "当前资金:",
            round(
                self.balance,
                2
            )
        )


        print(
            "交易记录:",
            len(self.trades)
        )


        print("======================")