import requests
import time



def get_markets(limit=500):


    url = "https://gamma-api.polymarket.com/markets"



    headers = {

        "User-Agent":
        "Polymarket-AI-Bot/1.0"

    }



    params = {

        "limit": limit

    }




    for i in range(5):


        try:


            response = requests.get(

                url,

                headers=headers,

                params=params,

                timeout=20

            )



            response.raise_for_status()



            data = response.json()




            if not isinstance(data, list):


                print(
                    "❌ API返回数据格式错误"
                )


                return []




            print(
                "✅ API连接成功"
            )



            return data




        except Exception as e:



            print(
                f"❌ 第{i+1}次连接失败"
            )


            print(e)



            time.sleep(3)





    print(
        "❌ API连接失败"
    )


    return []