import pickle
import os
import pandas as pd
import filecmp
import random

from bs4 import BeautifulSoup

directory = './raw_data/cambridge_raw_data'

print('Processing Cambridge words...')
for filename in os.listdir(directory):
    data = pickle.load(open(os.path.join(directory, filename), 'rb'))
    soup = BeautifulSoup(data, 'html.parser')

    word_list, pos_list, dfn_list = [], [], []
    # filter through every 'block' to find POS and definition
    for block_html in soup.select('.pr.entry-body__el'):
        word = block_html.select('.hw.dhw')[0].text

        pos = block_html.select('.pos.dpos')[0].text if block_html.select('.pos.dpos') else 'N/A'
        
        def_html = block_html.select('.def.ddef_d.db')
        dfns = [d.text.replace('\n', ' ') for d in def_html]
        if not dfns:
            print(word)
            continue
        word_list += [word]*len(dfns)
        pos_list += [pos]*len(dfns)
        dfn_list += dfns
    
    # possible issues -> typos on HTML page that do not have spaces
    df = pd.DataFrame({
        'word': word_list,
        'pos': pos_list,
        'dfns': dfn_list
    })

    df.to_csv('./cambridge_words_3000.csv', mode='a', index=False, header=False)
print('Finished parsing all the Cambridge words!')
    