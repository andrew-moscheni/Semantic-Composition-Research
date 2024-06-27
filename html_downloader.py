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
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.2420.81',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:124.0) Gecko/20100101 Firefox/124.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux i686; rv:124.0) Gecko/20100101 Firefox/124.0'
]
colors = ['red', 'cyan', 'green', 'yellow', 'magenta']
directory_names = ['mw', 'dict_dot_com', 'cambridge', 'free', 'online_api']

# declare fetch_html function (to be used by multiple threads)
def fetch_html(index):
    cprint(f'Processing {directory_names[index]}...', colors[index])
    proxies = [x[:-1] for x in requests.get('https://pastebin.com/raw/VJwVkqRT').text.split('\n')[2:]]
    proxy_cycle = cycle(random.sample(proxies, len(proxies)))
    agents_cycle = cycle(random.sample(user_agents, len(user_agents)))
    
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
            user = next(agents_cycle)

            # get the HTML and extract it from the response
            response = requests.get(url, headers={'User-Agent':user}, proxies={'http':proxy})
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
            time.sleep(random.uniform(1,3))
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