import requests


BOT_TOKEN = "8824563789:AAEZiUFy-uHi0HxOS4LQ_HxiOpHsfekhGoA"

CHAT_ID = "5560144147"



def send_message(message):


    url = (
        f"https://api.telegram.org/"
        f"bot{BOT_TOKEN}/sendMessage"
    )


    data = {

        "chat_id": CHAT_ID,

        "text": message

    }


    session = requests.Session()


    # 不读取Windows系统代理
    session.trust_env = False



    response = session.post(

        url,

        data=data,

        proxies={

            "http": "http://192.168.1.2:1082",

            "https": "http://192.168.1.2:1082"

        },

        timeout=20

    )


    return response.json()