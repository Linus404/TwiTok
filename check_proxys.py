import requests
import socket
import threading
from tqdm import tqdm

def get_real_ip():
    """
    Get the real IP address of the machine.
    """
    try:
        ip_url = "http://httpbin.org/get"
        response = requests.get(ip_url)
        real_ip = response.json()["origin"]
    except requests.exceptions.RequestException:
        # Failed to get real IP address, use local IP as fallback
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        real_ip = s.getsockname()[0]
        s.close()
    return real_ip

def check_proxy(proxy, real_ip, valid_proxies):
    """
    Check if a proxy is valid.
    """
    try:
        ip_check_url = "http://httpbin.org/get"
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        response = requests.get(ip_check_url, proxies=proxies, timeout=5)
        json_data = response.json()
        client_ip = json_data.get("origin")
        forwarded_for = json_data.get("headers", {}).get("X-Forwarded-For")
        
        if client_ip and client_ip != real_ip:
            # Check if X-Forwarded-For header is present and contains the real IP
            if not forwarded_for or real_ip not in forwarded_for:
                valid_proxies.append(proxy)
    except (requests.exceptions.RequestException, ValueError):
        pass

def validate_proxies(proxy_list_file, valid_proxies_file):
    """
    Validate proxies from a file and save valid proxies to a new file.
    """
    real_ip = get_real_ip()
    valid_proxies = []

    # Clear the contents of the valid_proxies_file
    with open(valid_proxies_file, "w") as f:
        f.write("")

    with open(proxy_list_file, "r") as f:
        proxies = f.read().split("\n")

    with tqdm(total=len(proxies), desc="Validating Proxies", unit=" proxies") as pbar:
        threads = []
        for proxy in proxies:
            if proxy.strip():  # Skip empty lines
                t = threading.Thread(target=check_proxy, args=(proxy, real_ip, valid_proxies))
                threads.append(t)
                t.start()

        for t in threads:
            t.join()
            pbar.update(1)

    with open(valid_proxies_file, "a") as f:
        f.write("\n".join(valid_proxies))

    print(f"Valid proxies saved to {valid_proxies_file}")

# Usage example
validate_proxies("proxy_list.txt", "valid_proxies.txt")