import requests
import time


def get_markets():

    url = "https://gamma-api.polymarket.com/markets"


    for i in range(5):

        try:

            response = requests.get(
                url,
                timeout=20
            )

            response.raise_for_status()


            print("✅ API连接成功")


            return response.json()


        except Exception as e:

            print(
                f"❌ 第{i+1}次连接失败"
            )

            print(e)

            time.sleep(3)



    print("❌ API连接失败")

    return []