# import dependencies
import pandas as pd
import os
import pickle

from bs4 import BeautifulSoup
from pattern.text.en import singularize

directory = './data_files/raw_data/mw_raw_data'

print('Processing MW words...')
for filename in os.listdir(directory):
    data = pickle.load(open(os.path.join(directory, filename), 'rb'))
    # get words, definitions, and part of speeches of words
    def_soup = BeautifulSoup(data, 'html.parser')

    # get the words, but keep them 'grouped' by container
    container = def_soup.select('.entry-word-section-container')
    defs = [[x.select('.hword'), x.select('.parts-of-speech'), x.select('.vg-sseq-entry-item ')] for x in container]
    new_list = [[d[0][0].text, d[1][0].text, [y.select('.dt')] if y.select('.dt') else [y.select('.un')]]
                for d in defs for y in d[2]]

    # useful lists for later checking
    words = [n[0] for n in new_list]
    pos = [n[1] for n in new_list]

    # make the definitions into text, combining forms
    variant = False
    formatted_defs = []
    for r in new_list:
        for d in r[2]:
            def_text = [d2.select('.unText') if d2.select('.unText') and not d2.select('.dtText')
                        else d2.select('.dtText') for d2 in d]
            try:
                def_string = ''.join([d2[0].text for d2 in def_text])
                formatted_defs.append([r[0], r[1], def_string])
            except:
                variant=True

    # make plural nouns singular if necessary
    word = filename.split('.')[0]
    single = singularize(word) if word[-1].islower() else word
    single_wrd = single if (word not in words) and (single in words) else word

    ret_word_list, ret_pos_list, ret_dfn_list = [], [], []
    if single_wrd in words:  # if the word matches, perfect!
        if not variant:
            subset = [s for s in formatted_defs if s[0] == single_wrd]
            ret_word_list = [s[0] for s in subset]
            ret_pos_list = [s[1] for s in subset]
            ret_dfn_list = [s[2] for s in subset]

        # variant spelling of word
        if not ret_dfn_list and not ret_pos_list or variant:
            dfn_list = [ct.select('.cxl-ref') for ct in container]
            ret_dfn_list = [x.text for y in dfn_list for x in y]
            ret_pos_list = ['variant'] * len(ret_dfn_list)
            ret_word_list = [word] * len(ret_dfn_list)

    else:  # either a variant on spelling, a verb tense, or another form
        # if verb tense, then it would be in the container (find indices of definitions)
        tenses = [x.select('.if') for _, x in enumerate(container)]
        other_list = [[x.text for x in y] for y in tenses]
        ret_word_list = [word]

        # if not a tense, then it must be another form
        if not any(word in sublist for sublist in other_list):
            variant = [x.select('.va') for _, x in enumerate(container)]
            other_list = [[x.text for x in y] for y in variant]

            # check if variation is in one definition or in whole entry
            in_def = [x.select('.vg .va') for _, x in enumerate(container)]
            in_def_list = [[x.text for x in y] for y in in_def]
            in_def_index = [i for i, x in enumerate(in_def_list) if word in x]

            # case that the word is in only one definition
            if in_def_index:
                ret_dfn_list = formatted_defs[in_def_index[0]][2]

        # different word, different pos, same defs
        if not any(word in sublist for sublist in other_list):
            variant = [x.select('.fw-bold.ure') for _, x in enumerate(container)]
            variant_pos = [x.select('.fw-bold.fl') for _, x in enumerate(container)]
            other_list = [[x.text for x in y] for y in variant]
            other_pos_list = [[x.text for x in y] for y in variant_pos]
            for i in range(len(other_list)):
                for j in range(len(other_list[i])):
                    if word in other_list[i][j]:
                        ret_pos_list = [other_pos_list[i][j]]
            ret_word_list = [word]

        # make a list of lists describing what definitions correspond to what containers
        i = 0
        groupings = []
        for ct in container:
            sub_list = []
            for _ in ct.select('.vg-sseq-entry-item'):
                sub_list.append(i)
                i += 1
            groupings.append(sub_list)

        # get container index and then get the associated groupings
        if not any([word in x for x in other_list]):
            continue
        container_index = [i for i, x in enumerate(other_list) if word in x][0]
        ret_pos_list = [container[container_index].select('.parts-of-speech')[0].text]
        ret_dfn_list = [s[2] for s in formatted_defs]
        ret_dfn_list = [ret_dfn_list[g] for g in groupings[container_index]]
        ret_word_list = ret_word_list * len(ret_dfn_list)
        ret_pos_list = ret_pos_list * len(ret_dfn_list)

    ret_dfn_list = [r.lstrip('\"').rstrip('\"').lstrip(': ') for r in ret_dfn_list]
    # make a DataFrame and then append it to pre-existing file
    df = pd.DataFrame({
        'word': ret_word_list,
        'pos': ret_pos_list,
        'dfn': ret_dfn_list
    })

    df.to_csv('./mw_words_3000.csv', mode='a', index=False, header=False)
print('Finished parsing all of the MW words!')
