from api_client import get_markets
from scanner import show_top_markets
from portfolio import Portfolio


def main():

    print("======================")
    print("🤖 Polymarket AI Bot 启动")
    print("======================")


    # 创建模拟账户

    account = Portfolio(100)



    # 获取市场

    markets = get_markets()


    if not markets:

        print("没有获取到市场数据")

        return



    print()

    print(
        "获取市场数量:",
        len(markets)
    )


    print()


    # AI扫描市场

    show_top_markets(
        markets
    )



    print()


    # 输出资金情况

    account.report()



if __name__ == "__main__":

    main()