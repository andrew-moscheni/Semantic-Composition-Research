"""
    A multithreaded application designed to extract and download HTML from relevant sites to be used
    in the model. Each thread will correspond to a different site and as of now will operate on the 
    <OXFORD 3000> words list.
"""

import requests
import pickle
import random
import time
import json
import threading

from itertools import cycle
from bs4 import BeautifulSoup
from termcolor import cprint


proxy_sites = [
    'https://free-proxy-list.net/uk-proxy.html',
    'https://www.sslproxies.org/',
    'https://www.us-proxy.org/',
    'https://free-proxy-list.net/'
]
url_stems = [
    'https://merriam-webster.com/dictionary/',                   # MW Dictionary
    'https://www.dictionary.com/browse/',                        # Dictionary.com
    'https://dictionary.cambridge.org/dictionary/english/',      # Cambridge Dictionary
    'https://www.thefreedictionary.com/',                        # Free Dictionary
    'https://api.dictionaryapi.dev/api/v2/entries/en/'           # Free Online Dictionary API
]
colors = ['red', 'cyan', 'green', 'yellow', 'magenta']
directory_names = ['mw', 'dict_dot_com', 'cambridge', 'free', 'online_api']
headers={'User-Agent': 'Mozilla/5.0 (Windows Phone 10.0; Android 6.0.1; Microsoft; RM-1152) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Mobile Safari/537.36 Edge/15.15254'}

# declare fetch_html function (to be used by multiple threads)
def fetch_html(index):
    cprint(f'Processing {directory_names[index]}...', colors[index])
    proxies = [x[:-1] for x in requests.get('https://pastebin.com/raw/VJwVkqRT').text.split('\n')[2:]]
    proxy_cycle = cycle(random.sample(proxies, len(proxies)))
    
    # for every word get the raw data (JSON or HTML) and store it in its correct directory
    with open('./oxford_3000/oxford_words.txt','r', encoding='utf-8') as f:
        for line in f.readlines():
            word = line.rstrip('\r\n').replace(u'\xa0', u' ')
            if ' ' in word:
                continue
            is_not_api = index < 4
            url = url_stems[index]+word
            directory = './raw_data/'+directory_names[index]+'_raw_data'
            filename = word + '.pickle' if is_not_api else word + '.json'
            mode = 'wb' if is_not_api else 'w'

            # cycle through the proxy list
            proxy = next(proxy_cycle)

            # get the HTML and extract it from the response
            response = requests.get(url, headers=headers, proxies={'http':proxy})
            if response.status_code != 200:
                if response.status_code == 404:
                    continue
                cprint(f'{url}:{response.status_code}', colors[index])
                raise RuntimeError(f'HTTP {response.status_code} Error.')

            raw_data = response.text if is_not_api else response.json()
            with open(directory + '/' + filename, mode) as file:
                if is_not_api:
                    pickle.dump(raw_data, file)
                else:
                    json.dump(raw_data, file)
            time.sleep(random.uniform(1,6))
    cprint(f'Finished processing {directory_names[index]}!', colors[index])


# pretty printing -- converts seconds to hours, minutes, seconds
def seconds_conversion(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f'{int(h):d}:{int(m):02d}:{int(s):02d}'


if __name__ == '__main__':
    # split the URLs among many threads using range function and map
    t1 = time.time()
    threads = []
    for i in range(len(url_stems)):
        threads.append(threading.Thread(target=fetch_html, args=(i,)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f'Downloading completed successfully in {seconds_conversion(time.time()-t1)} (hours:minutes:seconds)')