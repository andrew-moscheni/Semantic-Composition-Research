import pickle
import os
import pandas as pd
import filecmp
import random

from bs4 import BeautifulSoup

directory = './raw_data/free_raw_data'
filename = 'a.pickle'
data = pickle.load(open(os.path.join(directory, filename), 'rb'))
soup = BeautifulSoup(data, 'html.parser')

name = soup.select('h2')
print(name)
block_html = soup.select('.pseg')
print([b.text for b in block_html[0].select('.ds-list')])
print(len(name))
print(len(block_html))
print(len(name)==len(block_html))