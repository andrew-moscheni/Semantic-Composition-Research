# import any dependencies
import json
import pandas as pd
import os

# name of the directory the files are under
directory = './data_files/raw_data/online_api_raw_data'

# filter through every file and extract the information from the JSON file
for filename in os.listdir(directory):
    data = json.load(open(os.path.join(directory, filename)))

    for d in data:
        word = d['word']
        pos = d['meanings'][0]['partOfSpeech']

        for def_list in d['meanings'][0]['definitions']:
            dfn = def_list['definition']
            df = pd.DataFrame({
                'word': [word],
                'pos': [pos],
                'dfn': [dfn]
            })
            df.to_csv('./online_api_words_3000.csv', mode='a', index=False, header=False)