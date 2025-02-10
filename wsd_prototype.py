import pandas as pd
import numpy as np
import nltk
import torch
from flair.data import Sentence
from sentence_transformers import SentenceTransformer
from flair.embeddings import TransformerWordEmbeddings

import warnings


def wsd_and_pos_prototype(sent, word, embedding_type='bert-base-uncased'):
    # run the sentence through NLTK's POS tagger
    text = nltk.tokenize.word_tokenize(sent)
    poses = nltk.pos_tag(text)
    # get the word and POS from the tokenizer
    word,pos = [tup for tup in poses if tup[0]==word][0]
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
    else:
        return []
    # find definitions that match POS and word
    definition = defs.loc[(defs['word'] == word) & (defs['pos'] == pos), 'dfns']
    if len(definition) == 0:
        return []
    else:
        definition = definition.values[0]
    # use the intfloat/e5-large-v2 model since it performed best on MTEB
    model = SentenceTransformer('intfloat/e5-large-v2')
    word_embed = TransformerWordEmbeddings(embedding_type)

    # get all the embeddings from the Transformers
    e_wrd = torch.tensor(word_embed.embed(Sentence(word)))
    e_sent = torch.tensor(model.encode(Sentence(sent)))
    e_dfn = torch.tensor(model.encode(Sentence(definition)))
    return e_dfn, e_wrd, e_sent

# list embedding types here
embedding_types = []
samp_sent = pd.read_csv('./cambridge_sample_sentences.csv')
for embed_type in embedding_types:
    e_words, e_dfns, diffs = [], [], [] # empty lists to become dataframes
    for _,row in samp_sent.iterrows():
        tup = wsd_and_pos_prototype(row['sentence'],row['word'],embed_type)
        if tup == []: # check if definitions exist
            e_dfn,e_wrd,_ = tup
        e_words.append(e_wrd)
        e_dfns.append(e_dfn)
        diffs.append(e_dfn-e_wrd)
    # format as definitions
    df = pd.DataFrame({
        'e_wrd': e_words,
        'e_def': e_dfns,
        'e_def-e_wrd': diffs
    })
    # create the file only if it does not exist
    df.to_csv(f'./diff_model_csvs/{embed_type}.csv', index=False, mode='x')
