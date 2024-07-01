import requests

response = requests.get('https://pastebin.com/raw/VJwVkqRT')
for line in response.text.split('\r\n')[2:]:
    check = requests.get('https://ip.oxylabs.io/location', proxies={'http':'http://'+line})
    if check.status_code == 200:
        with open('./proxies.txt', 'a') as f:
            f.write(line+'\n')