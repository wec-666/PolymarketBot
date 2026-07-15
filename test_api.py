import requests

response = requests.get("https://www.baidu.com")

print("状态码：", response.status_code)