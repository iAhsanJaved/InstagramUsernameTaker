import requests
import json
import threading
import time
import random
import re
from urllib.parse import urlencode

targets = []
# deal with config.json
with open("config.json") as file:
    config = json.load(file)

with open("usernames_list.txt", "r") as file:
    targets = file.read().splitlines() 

email = config['email']
username = config['username']
password = config['password']
list_of_ua = config.get("list_of_ua")
#targets = config['targetUsernames']

user_agent = random.sample(list_of_ua, 1)[0]

def changeUsername(availableUsername):
    s = requests.Session()
    s.headers.update({
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Host": "www.instagram.com",
        "Origin": "https://www.instagram.com",
        "Referer": "https://www.instagram.com/",
        "User-Agent": user_agent,
        "X-Instagram-AJAX": "1",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
    })

    login_post = {
        "username": username,
        "password": password,
    }
    r = s.get('https://www.instagram.com/')
    csrf_token = re.search('(?<="csrf_token":")\w+', r.text).group(0)
    s.headers.update({"X-CSRFToken": csrf_token})
    time.sleep(5 * random.random())
    
    url_login = "https://www.instagram.com/accounts/login/ajax/"
    login = s.post(url_login, data=login_post, allow_redirects=True)

    if login.status_code not in (200, 400):
        print("[{0}] Login failed!".format(username))
        print("Response Status: {login.status_code}")
    else:
        loginResponse = login.json()
        csrftoken = login.cookies["csrftoken"]
        s.headers.update({"X-CSRFToken": csrftoken})
        
        if loginResponse.get("errors"):
            print("Something is wrong with Instagram! Please try again later...")
            print(loginResponse["errors"]["error"])
        elif loginResponse.get("message") == "checkpoint_required":
            print('[{0}] checkpoint required!'.format(username))
        elif loginResponse.get("authenticated") is False:
            print("Login error! Check your login data!")
            return
        else:
            rollout_hash = re.search('(?<="rollout_hash":")\w+', r.text).group(0)
            s.headers.update({"X-Instagram-AJAX": rollout_hash})
            successfulLogin = True
            # ig_vw=1536; ig_pr=1.25; ig_vh=772;  ig_or=landscape-primary;
            s.cookies["csrftoken"] = csrftoken
            s.cookies["ig_vw"] = "1536"
            s.cookies["ig_pr"] = "1.25"
            s.cookies["ig_vh"] = "772"
            s.cookies["ig_or"] = "landscape-primary"
            time.sleep(5 * random.random())
        
        if successfulLogin:
            r = s.get("https://www.instagram.com/")
            csrftoken = re.search('(?<="csrf_token":")\w+', r.text).group(0)
            s.cookies["csrftoken"] = csrftoken
            s.headers.update({"X-CSRFToken": csrftoken})
            finder = r.text.find(username)
            if finder != -1:
                print("[{0}] Login succeeded!".format(username))
                url_edit = "https://www.instagram.com/accounts/edit/"
                r = s.get("https://www.instagram.com/")
                csrftoken = re.search('(?<="csrf_token":")\w+', r.text).group(0)
                s.cookies["csrftoken"] = csrftoken
                s.headers.update({"X-CSRFToken": csrftoken})
                formData = {
                    'first_name': 'NMadvcwc',
                    'email': email,
                    'username': availableUsername,
                    'phone_number':'',
                    'biography':'',
                    'external_url':'',
                    'chaining_enabled': 'on'
                }
                rf = s.post(url_edit, data=formData)
                print(rf)
            else:
                print("Login error! Check your login data!")
                
        else:
            print("Login error! Connection error!")
    pass


def checkUsername(targetUsername):
    global stop_threads
    #start monitoring the username    
    while not stop_threads:
        usernameURL = 'https://www.instagram.com/web/search/topsearch/?'+ urlencode({
            'context':'blended', 'query':targetUsername, 'rank_token':'0.395359231827089', 'count':'1'
            })
        res = requests.get(usernameURL)
        json_data = json.loads(res.text)
        
        if res.status_code == 200:
            if len(json_data['users']) == 0:
                print('[{0}] is available!!!'.format(targetUsername))
                changeUsername(targetUsername)
                print('[{0}] Completed Turbo Killing Thread'.format(targetUsername))
                stop_threads = True
                break
            else:
                print('[{0}] is not available'.format(json_data['users'][0].get("user").get("username")))



if __name__ == '__main__':
    print("Instagram Username Taker")
    print("=" * 60)
    print("Username: {}".format(username))
    print("Password: {}".format("*" * len(password)))
    print("# Of Targets: {}".format(str(len(targets))))
    #print(f"Endpoint: {endpoint}")
    print("=" * 60)
    print("")
    print(targets)
    stop_threads = False
    tin = input("Would you like to start (y/n)?: ")
    if tin.lower() == "y":
        for x in targets:
            t = threading.Thread(target=checkUsername, args=(x,))
            t.start()
    else:
        exit()
