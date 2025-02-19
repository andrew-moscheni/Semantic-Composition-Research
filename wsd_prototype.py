import pandas as pd
import numpy as np
import nltk
import torch
#from flair.data import Sentence
from sentence_transformers import SentenceTransformer
from nltk.corpus import wordnet
#from flair.embeddings import TransformerWordEmbeddings

import warnings


def wsd_and_pos_prototype(sent, word, model):
    # run the sentence through NLTK's POS tagger and lemmatizer 
    lemmatizer = nltk.stem.WordNetLemmatizer()
    words = nltk.word_tokenize(sent.lower())
    pos_tags = nltk.pos_tag(words)
    
    # Lemmatize based on POS tags
    poses = []
    for wrd, tag in pos_tags:
        # Map NLTK POS tags to WordNet POS tags
        if tag.startswith('NN'):
            wordnet_pos = wordnet.NOUN
        elif tag.startswith('VB'):
            wordnet_pos = wordnet.VERB
        elif tag.startswith('JJ'):
            wordnet_pos = wordnet.ADJ
        else:
            wordnet_pos = wordnet.NOUN  # Default to NOUN for simplicity
        
        # Lemmatize the word
        lemmatized_word = lemmatizer.lemmatize(wrd, pos=wordnet_pos)
        poses.append((lemmatized_word, tag))

    # get the word and POS from the tokenizer
    tuples = [tup for tup in poses if tup[0]==word]
    if not tuples:
        return []
    else:
        word,pos = tuples[0]
    # find the matching word and verb sense from the filtered MW definitions
    defs = pd.read_csv('./data_files/filtered_files/mw_words_filtered.csv')
    # convert POS tags to words (so we can do filtering easier)
    if 'JJ' in pos:
        pos='adjective'
    elif 'NN' in pos:
        pos='noun'
    elif 'RB' in pos:
        pos='adverb'
    elif 'VB' in pos:
        pos='verb'
    elif pos=='DT':
        pos='determiner'
    else:
        pos='noun' # for simplicity
    # find definitions that match POS and word
    definition = defs.loc[(defs['word'] == word) & (defs['pos'] == pos), 'dfns']
    if len(definition) == 0:
        return []
    else:
        definition = definition.values[0]
    # get all the embeddings from the Sentence Transformer
    e_wrd = torch.tensor(model.encode(word))
    e_sent = torch.tensor(model.encode(sent))
    e_dfn = torch.tensor(model.encode(definition))
    return e_dfn, e_wrd, e_sent

# embeddings and file names
embedding_types = ['sentence-transformers/stsb-roberta-large', 'intfloat/e5-large-v2', 'facebook/bart-large']
names = ['roberta-large', 'intfloat-e5', 'facebook-bart']
samp_sent = pd.read_csv('./cambridge_sample_sentences.csv')
curr_letter = 'z'

for (embed_type, name) in zip(embedding_types, names):

    # initialize the model before sending it into the function
    print(f'running embedding type: {embed_type}')
    model = SentenceTransformer(embed_type)
    e_words, e_dfns, diffs = [], [], [] # empty lists to become dataframes

    for _,row in samp_sent.iterrows():
        wrd = row['word']
        if not wrd.startswith(curr_letter):
            print(f'\tCurrently on letter {wrd[0]}')
            curr_letter = wrd[0]
        tup = wsd_and_pos_prototype(row['sentence'],row['word'],model)
        if not tup: # check if definitions exist
            continue
        e_dfn,e_wrd,_ = tup
        e_words.append([t.item() for t in e_wrd])
        e_dfns.append([t.item() for t in e_dfn])
        diffs.append([t.item() for t in (e_dfn-e_wrd)])
    # format as definitions
    df = pd.DataFrame({
        'e_wrd': e_words,
        'e_def': e_dfns,
        'e_def-e_wrd': diffs
    })
    # create the file only if it does not exist
    df.to_csv(f'./{name}.csv', index=False, mode='x')
    print(f'finished running embedding type: {embed_type}')
