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

from concurrent.futures import ThreadPoolExecutor


# GLOBAL VARIABLES
MAX_PAGES_PER_MIN = 5
MAX_PAGES_BEFORE_RESET = 20
url_stems = [
    'https://merriam-webster.com/dictionary/',                   # MW Dictionary
    'https://www.dictionary.com/browse/',                        # Dictionary.com
    'https://dictionary.cambridge.org/dictionary/english/',      # Cambridge Dictionary
    'https://www.collinsdictionary.com/us/dictionary/english/',  # Collins English Dictionary
    'https://api.dictionaryapi.dev/api/v2/entries/en/'           # Free Online Dictionary API
]
directory_names = ['mw', 'dict_dot_com', 'cambridge', 'online_api', 'collins']
word_list = open('./oxford_3000/oxford_words.txt', 'r').read().split('\n')


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

        response = requests.get(url)
        if response.status_code > 229:
            raise RuntimeError(f'HTTP {response.status_code} Error.')

        raw_data = response.text if is_not_api else response.json()
        with open(directory + '/' + filename, mode) as file:
            pickle.dump(raw_data, file) if is_not_api else json.dump(raw_data, file)

        # randomize request time
        page_counter_before_reset += 1
        if page_counter_before_reset >= MAX_PAGES_PER_MIN:
            time.sleep(60-time_used_before_reset)
            page_counter_before_reset, time_used_before_reset = 0, 0
        elif total_pages_before_reset >= MAX_PAGES_BEFORE_RESET and total_time_used_before_reset <= 240:
            time.sleep(240-total_time_used_before_reset)
            page_counter_before_reset, time_used_before_reset = 0, 0
            total_pages_before_reset, total_time_used_before_reset = 0, 0
        else:
            sleep_time = random.randint(8,10)
            time.sleep(sleep_time)
            total_time_used_before_reset += sleep_time
            time_used_before_reset += sleep_time
    print(f'Finished processing {directory_names[index]}!')


# pretty printing -- converts seconds to days, hours, minutes, seconds
def seconds_conversion(seconds):
    seconds = seconds % (24 * 3600)
    days = seconds // 86400
    seconds %= 86400
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
     
    return "%d:%02d:%02d:%02d" % (days, hour, minutes, seconds)


if __name__ == '__main__':
    # split the URLs among many threads using range function and map
    t1 = time.time()
    with ThreadPoolExecutor(max_workers=len(url_stems)) as executor:
        executor.map(fetch_html, range(len(url_stems)))
    print(f'Execution completed successfully in {seconds_conversion(time.time()-t1)} \
        (days: hours:minutes:seconds)')