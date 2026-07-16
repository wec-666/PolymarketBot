import time
from bot import run_bot


print("======================")
print("⏰ Polymarket自动监控启动")
print("======================")


while True:

    try:

        run_bot()


    except Exception as e:

        print("运行错误:")
        print(e)



    print()

    print("等待5分钟重新扫描...")


    time.sleep(300)