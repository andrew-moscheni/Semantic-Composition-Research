# import any dependencies
import pickle
import os
import pandas as pd

from bs4 import BeautifulSoup

directory = './raw_data/dict_dot_com_raw_data'
filename = 'a.pickle'
data = pickle.load(open(os.path.join(directory, filename), 'rb'))
soup = BeautifulSoup(data, 'html.parser')

i=1
while soup.select(f'div[id="dictionary-entry-{i}"]'):
    block_html = soup.select(f'div[id="dictionary-entry-{i}"]')[0]
    word = block_html.select('.bZjAAKVoBi7vttR0xUts h1,p')[0].text

    pos = block_html.select('.S3nX0leWTGgcyInfTEbW h2')[0].text if \
        block_html.select('.S3nX0leWTGgcyInfTEbW h2') else 'N/A'
            
    def_html = block_html.select('ol .NZKOFkdkcvYgD3lqOIJw div')
    dfns = [d.text.replace('\n', ' ') for d in def_html]

    print(word)
    print(pos)
    print(dfns)
    i+=1