# import dependencies
import pandas as pd
import os
import pickle

from bs4 import BeautifulSoup

directory = './data_files/raw_data/cambridge_raw_data'

print('Processing Cambridge sample sentences...')
for filename in os.listdir(directory):
    data = pickle.load(open(os.path.join(directory, filename), 'rb'))
    soup = BeautifulSoup(data, 'html.parser')
    container = soup.select('.pr.entry-body__el')
    pos = [c.select('.pos.dpos') for c in container]
    sent_cont = [c.select('.def-body.ddef_b') for c in container]
    pos_lst = []
    sentences = []
    for p, s in zip(pos, sent_cont):
        if not ([c.select('.examp.dexamp')[0] for c in s if c.select('.examp.dexamp')] and p):
            continue
        sent_lst = [c.select('.examp.dexamp')[0] for c in s if c.select('.examp.dexamp')]
        sentence = [s.select('.eg.deg')[0].text for s in sent_lst]
        sentences+=sentence
        pos_lst+=[p[0].text]*len(sentence)
    
    len(pos_lst)
    len(sentences)
    df = pd.DataFrame({
        'word': [filename.split('.')[0]]*len(sentences),
        'pos': pos_lst,
        'sentence': sentences
    })

    df.to_csv('./cambridge_sample_sentences.csv', mode='a', index=False, header=False)
print('Finished parsing Cambridge sample sentences!')