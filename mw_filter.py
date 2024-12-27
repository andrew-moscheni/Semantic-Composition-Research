import pandas as pd
import re

mw_csv = pd.read_csv('./data_files/cleaned_files/mw_words_3000.csv')
mw_csv['pos'] = mw_csv['pos'].apply(lambda wrd: (re.sub(r'\(\d+\)','',wrd)).rstrip())
newdf=mw_csv.drop_duplicates(subset=['word', 'pos'], keep='first')
newdf.to_csv('./data_files/filtered_files/mw_words_filtered.csv', index=False)