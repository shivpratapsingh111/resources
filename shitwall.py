import requests
import json
import time
import os

# Use a session for requests
session = requests.Session()

def start_warnings():
    if is_cloudflare():
        print("[*] CAUTION: Cloudflare detected !!!")
        return False
    else:
        print("Continuing with Autoauth...")
        return True

def is_cloudflare():
    try:
        response = session.get("http://ipinfo.io/json").text
        return 'Cloudflare' in response
    except requests.exceptions.RequestException:
        print("Error in checking VPN status")
        return False

def is_login_required(detect_url):
    try:
        response = session.get(detect_url)
        return response.status_code !=  204
    except requests.exceptions.RequestException:
        print("Error in checking login status")
        return False

def create_config():
    print("Creating config file...")
    ui = os.getenv('UI', "YOUR_UID_HERE")
    passw = os.getenv('PASSW', "YOUR_PASSWORD_HERE")
    timeout = os.getenv('TIMEOUT', "3")
    with open(".shitwall.cfg", "w") as json_file:
        data = {"ui": ui, "passw": passw, "timeout": timeout}
        json.dump(data, json_file)

def read_config():
    try:
        with open('.shitwall.cfg', "r") as json_file:
            data = json.load(json_file)
            return data['ui'], data['passw'], data['timeout']
    except FileNotFoundError:
        print("[-] Config file not found")
        create_config()
        return read_config()
    except json.JSONDecodeError:
        print("[-] Config file is not in proper format")
        create_config()
        return read_config()

def login(ui, passw, magic_):
    tar_url = "http://172.15.15.1:1000/login?="
    data = {'username': ui, 'password': passw, 'magic': magic_, '4Tredir': "'"}
    try:
        response = session.post(url=tar_url, data=data)
        if 'Authentication Keepalive' in response.text:
            print('Done...')
            return True
        else:
            print('Wrong Password')
            return False
    except requests.exceptions.RequestException:
        print("Connection Error")
        return False

def main():
    if not start_warnings():
        return
    ui, passw, timeout = read_config()
    while True:
        try:
            if is_cloudflare():
                print("[*] VPN is active")
            if is_login_required("http://cloudflareportal.com/test"):
                print("[***] Login is required")
                if login(ui, passw, ''):
                    return True
                else:
                    return False
            else:
                print("\n[*] Login not required...")
                time.sleep(int(timeout))
                continue
        except KeyboardInterrupt:
            print("\nExiting...")
            os._exit(1)
            return
        except Exception as e:
            print("Error: " + str(e))
            print("Make sure you are connected to the college network and VPN/proxy is disabled")
            print("If done, press 'y' to continue")
            if input() != 'y':
                return
            print("Checking again in " + str(timeout) + " seconds")
            print("Waiting for next check...")
            time.sleep(int(timeout))

if __name__ == "__main__":
    while True:
        main()
