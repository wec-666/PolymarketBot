from api_client import get_markets
from scanner import show_top_markets
from portfolio import Portfolio
from trade_engine import TradeEngine
from trade_signal import generate_signal
from risk_manager import calculate_position
from telegram_bot import send_message

import time



print("======================")
print("🤖 Polymarket AI Bot启动")
print("======================")



# 创建资金账户

account = Portfolio(100)



# 创建交易引擎

engine = TradeEngine(account)




while True:


    try:


        print()
        print("🔍 开始扫描市场...")



        markets = get_markets()



        if not markets:


            print("❌ 没有获取到市场")


            time.sleep(300)

            continue




        # 获取评分最高市场

        top_markets = show_top_markets(
            markets
        )




        for item in top_markets:



            market = item["market"]

            score = item["score"]



            question = market.get(
                "question"
            )



            probability = market.get(
                "outcomePrices"
            )



            volume = float(
                market.get("volume") or 0
            )




            signal = generate_signal(
                probability,
                volume,
                score
            )



            print()

            print(
                "最终信号:",
                signal
            )




            # 只交易有效信号

            if signal in [
                "BUY_YES",
                "BUY_NO"
            ]:



                # 检查已有持仓

                if account.has_position(
                    question
                ):


                    print(
                        "⚠️ 已存在该市场持仓，跳过"
                    )


                    continue




                # 计算仓位

                amount = calculate_position(
                    account.balance
                )




                # Telegram通知


                message = f"""
🔥 Polymarket AI交易机会


市场:

{question}


方向:

{signal}


评分:

{score}


交易量:

{volume}


投入:

{amount}

"""



                try:


                    send_message(
                        message
                    )


                    print(
                        "📨 Telegram通知发送成功"
                    )


                except Exception as e:


                    print(
                        "⚠️ Telegram发送失败:",
                        e
                    )




                # 执行模拟交易


                engine.execute(

                    question,

                    signal,

                    amount

                )



                break





        account.report()



        print()

        print(
            "等待5分钟重新扫描..."
        )



        time.sleep(300)




    except KeyboardInterrupt:


        print()

        print(
            "🛑 Bot已停止"
        )

        break





    except Exception as e:


        print()

        print(
            "❌ 运行错误:"
        )


        print(e)



        time.sleep(60)