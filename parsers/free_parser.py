import pickle
import os
import pandas as pd
import filecmp
import random
import re

from bs4 import BeautifulSoup

directory = './data_files/raw_data/free_raw_data'

print('Processing TheFreeOnlineDictionary.com Words...')
for filename in os.listdir(directory):
    data = pickle.load(open(os.path.join(directory, filename), 'rb'))
    soup = BeautifulSoup(data, 'html.parser')

    # id="MainTxt" => section => h2 word, i POS, [div => ds_list/ds_single => sds_list (if nec.)]
    def_sections = soup.select("#Definition")[0]

    words=[]
    poss=[]
    dfns=[]
    # now get the word, POS, and the divs to the definitions
    for section in def_sections.find_all('section'):
        if section.get('data-src') not in ['hcUsage', 'hcVerbTblEn', 'shUnfW']:
            iter_word = section.find_all('h2')
            for section_words in iter_word:
                # ignore prefixes and suffixes
                word = re.sub(f'[0-9]| |\.', '', section_words.text)
                if word[0] == '-' or word[-1] == '-':
                    continue
                # if there is a comma in the word, then we take the first word in front of the commas
                if ',' in word:
                    word=word.split(',')[0]

                # get the container and the name of the container for the POS and the definition
                container = section_words.find_next('div')
                container_name = container.get('class')[0] if container.get('class') else None
                
                # check if the container name is pseg or if the container does not have a name
                if container_name == 'pseg' or not container_name:
                    container = container.find_next('div')
                    container_name = container.get('class')[0]

                pos = container.find_previous_sibling('i').text.replace('.','') if container.find_previous_sibling('i') is not None else 'N/A'

                if container_name == 'ds-single': # single definition
                    ex = container.find_next('span', attrs={'class': 'illustration'})
                    if ex:
                        ex.extract()
                    addit=container.find('i')
                    if addit:
                        addit.extract()

                    all_but_parenth = container.text.lstrip(' ').rstrip(' ').split('.')[0].replace('()','').split(':')[0]
                    final_string = re.sub(r'\([^()]*\)','',all_but_parenth,count=1).lstrip(' ').rstrip(' ')
                    if final_string.count(')') == final_string.count('('):
                        # add to df
                        df = pd.DataFrame({
                            'word': [filename.split('.')[0]],
                            'pos': [pos],
                            'dfn': [final_string]
                        })
                        df.to_csv('./data_files/parsed_data_files/free.csv', mode='a', index=False, header=False)
                else: # multiple definitions
                    parent_name = container.find_previous('h2')
                    parent_pos = container.find_previous_sibling('i').text.replace('.','') if container.find_previous_sibling('i') is not None else 'N/A'
                    curr_pos = parent_pos
                    while(container and parent_name == container.find_previous('h2') and parent_pos==curr_pos):
                        ex = container.find_next('span', attrs={'class': 'illustration'})
                        if ex:
                            ex.extract()
                        addit=container.find('i')
                        if addit:
                            addit.extract()
                        #go through any possible sublists (sdslist and parse)
                        if container.findChildren('div', attrs={'class': 'sds-list'}):
                            for child in container.findChildren('div', attrs={'class': 'sds-list'}):
                                no_letters = re.sub('[a-z]+\. ','',child.text)
                                all_but_parenth = no_letters.lstrip(' ').rstrip(' ').split('.')[0].replace('()','').split(':')[0]
                                final_string = re.sub(r'\([^()]*\)','',all_but_parenth,count=1).lstrip(' ').rstrip(' ')
                                if final_string.count(')') == final_string.count('('):
                                    # add to df
                                    df = pd.DataFrame({
                                        'word': [filename.split('.')[0]],
                                        'pos': [pos],
                                        'dfn': [final_string]
                                    })
                                    df.to_csv('./data_files/parsed_data_files/free.csv', mode='a', index=False, header=False)
                        else:
                            #remove numbers, anything past the period, (), first set of ()
                            no_numbers = re.sub('[0-9]+\.','',container.text)
                            all_but_parenth = no_numbers.lstrip(' ').rstrip(' ').split('.')[0].replace('()','').split(':')[0]
                            final_string = re.sub(r'\([^()]*\)','',all_but_parenth,count=1).lstrip(' ').rstrip(' ')
                            if final_string.count(')') == final_string.count('('):
                                # add to df
                                df = pd.DataFrame({
                                    'word': [filename.split('.')[0]],
                                    'pos': [pos],
                                    'dfn': [final_string]
                                })
                                df.to_csv('./data_files/parsed_data_files/free.csv', mode='a', index=False, header=False)
                        #print(''.join(container.find_all(string=True,recursive=False)))
                        container=container.find_next_sibling('div', class_='ds-list')
                        curr_pos = container.find_previous_sibling('i').text.replace('.','') if  container is not None and container.find_previous_sibling('i') is not None else 'N/A'

# OCTOBER 27, 2024
# TODO: 5. move on to the data-cleaning phase
