import requests
import random

with open("valid_proxies.txt", "r") as f:
    proxies = f.read().split("\n")
proxy = random.choice(proxies)
print("Proxy = %s" % proxy)

# Choose a proxy from your list of proxies
proxy = f"http://{proxy}"

# Example URL to test
url = "http://httpbin.org/ip"

# Set up the proxy in the requests library
proxies = {
    "http": proxy,
    "https": proxy
}

try:
    # Make a request using the proxy
    response = requests.get(url, proxies=proxies, timeout=5)
    
    # Check if the request was successful
    if response.status_code == 200:
        print("Proxy routing works. Your IP:", response.json()["origin"])
    else:
        print("Proxy routing failed.")
except requests.exceptions.RequestException as e:
    print("Proxy routing failed. Error:", e)