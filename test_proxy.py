import requests


print(
    requests.utils.get_environ_proxies(
        "https://api.telegram.org"
    )
)