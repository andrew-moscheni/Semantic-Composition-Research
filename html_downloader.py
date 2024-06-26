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

from concurrent.futures import ThreadPoolExecutor
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
    'https://www.collinsdictionary.com/us/dictionary/english/',  # Collins English Dictionary
    'https://api.dictionaryapi.dev/api/v2/entries/en/'           # Free Online Dictionary API
]
colors = ['red', 'cyan', 'green', 'yellow', 'magenta']
directory_names = ['mw', 'dict_dot_com', 'cambridge', 'online_api', 'collins']

# make the word list and the list of working proxies (to be used later)
word_list = open('./oxford_3000/oxford_words.txt', 'r').read().split('\n')
proxies = [x[:-1] for x in requests.get('https://pastebin.com/raw/VJwVkqRT').text.split('\n')[2:]]
proxy_cycle = cycle(generate_proxies())


# declare fetch_html function (to be used by multiple threads)
def fetch_html(index):
    cprint(f'Processing {directory_names[index]}...', colors[index])
    
    # for every word get the raw data (JSON or HTML) and store it in its correct directory
    for word in word_list:

        is_not_api = index < 4
        url = url_stems[index]+word
        directory = './'+directory_names[index]+'_raw_data'
        filename = word + '.pickle' if is_not_api else word + '.json'
        mode = 'wb' if is_not_api else 'w'

        # cycle through the proxy list
        proxy = next(proxy_cycle)

        # get the HTML and extract it from the response
        response = requests.get(url, proxies={'http':proxy})
        if response.status_code != 200:
            raise RuntimeError(f'HTTP {response.status_code} Error.')

        raw_data = response.text if is_not_api else response.json()
        with open(directory + '/' + filename, mode) as file:
            pickle.dump(raw_data, file) if is_not_api else json.dump(raw_data, file)
    cprint(f'Finished processing {directory_names[index]}!', colors[index])


# pretty printing -- converts seconds to hours, minutes, seconds
def seconds_conversion(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f'{h:d}:{m:02d}:{s:02d}'


if __name__ == '__main__':
    # split the URLs among many threads using range function and map
    t1 = time.time()
    with ThreadPoolExecutor(max_workers=len(url_stems)) as executor:
        executor.map(fetch_html, range(len(url_stems)))
    print(f'Downloading completed successfully in {seconds_conversion(time.time()-t1)} \
        (hours:minutes:seconds)')