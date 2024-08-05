# import any dependencies
import pickle
import os
import pandas as pd
import re

from bs4 import BeautifulSoup

directory = './raw_data/dict_dot_com_raw_data'

print('Processing Dictionary.com Words...')
for filename in os.listdir(directory):
    data = pickle.load(open(os.path.join(directory, filename), 'rb'))
    soup = BeautifulSoup(data, 'html.parser')

    word_list, pos_list, dfn_list = [], [], []

    i=1
    while soup.select(f'div[id="dictionary-entry-{i}"]'):
        block_html = soup.select(f'div[id="dictionary-entry-{i}"]')[0]
        word = block_html.select('.bZjAAKVoBi7vttR0xUts h1,p')[0].text

        pos = block_html.select('.S3nX0leWTGgcyInfTEbW h2')[0].text if \
            block_html.select('.S3nX0leWTGgcyInfTEbW h2') else 'N/A'
                
        def_html = block_html.select('ol .NZKOFkdkcvYgD3lqOIJw div')
        dfns = [d.text.replace('\n', ' ') for d in def_html]

        word_list += [word]*len(dfns)
        pos_list += [pos]*len(dfns)
        dfn_list += dfns

        i+=1

    df = pd.DataFrame({
        'word': word_list,
        'pos': pos_list,
        'dfns': dfn_list
    })

    df.to_csv('./dict_dot_com_words_3000.csv', mode='a', index=False, header=False)
print('Finished parsing all the Dictionary.com words!')