"""
    A multithreaded application designed to extract and download HTML from relevant sites to be used
    in the model. Each thread will correspond to a different site and as of now will operate on the 
    <OXFORD 3000> words list.
"""

# packages/dependencies here
import requests
import pickle
import random
import time
import json

from concurrent.futures import ThreadPoolExecutor
from itertools import cycle
from bs4 import BeautifulSoup


# GLOBAL VARIABLES
MAX_PAGES_PER_MIN = 5
MAX_PAGES_BEFORE_RESET = 20
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
directory_names = ['mw', 'dict_dot_com', 'cambridge', 'online_api', 'collins']

# make the word list and the list of working proxies (to be used later)
def generate_proxies():
    print('Generating proxies...')
    proxy_list = set()
    for site in proxy_sites:
        response = requests.get(site)
        soup = BeautifulSoup(response.text)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0'}
        # go through the rows of the table
        for row in soup.select('.table.table-striped.table-bordered tbody tr'):
            # get the proxy
            ip, port = row.select('td')[0:2]
            schematic = 'https' if row.select('td')[6] == 'yes' else 'http'
            proxy={schematic:schematic+'://'+ip.text+':'+port.text}
            # test it
            check = requests.get('https://www.nhl.com/', headers=headers, proxies=proxy)
            if check.status_code == 200:
                proxy_list.add(proxy)
    print('Finished generating proxies!')
    return proxy_list

word_list = open('./oxford_3000/oxford_words.txt', 'r').read().split('\n')
proxy_cycle = cycle(generate_proxies())


# declare fetch_html function (to be used by multiple threads)
def fetch_html(index):
    print(f'Processing {directory_names[index]}...')
    # randomization variables
    total_pages_before_reset, page_counter_before_reset = 0, 0
    time_used_before_reset, total_time_used_before_reset = 0, 0
    
    # for every word get the raw data (JSON or HTML) and store it in its correct directory
    for word in word_list:
        is_not_api = index < 4
        url = url_stems[index]+word
        directory = './'+directory_names[index]+'_pages'
        filename = word + '.pickle' if is_not_api else word + '.json'
        mode = 'wb' if is_not_api else 'w'
        # cycle through the proxy list
        proxy = next(proxy_cycle)

        response = requests.get(url, proxies=proxy)
        if response.status_code > 229:
            raise RuntimeError(f'HTTP {response.status_code} Error.')

        raw_data = response.text if is_not_api else response.json()
        with open(directory + '/' + filename, mode) as file:
            pickle.dump(raw_data, file) if is_not_api else json.dump(raw_data, file)
    print(f'Finished processing {directory_names[index]}!')


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
    print(f'Execution completed successfully in {seconds_conversion(time.time()-t1)} \
        (hours:minutes:seconds)')