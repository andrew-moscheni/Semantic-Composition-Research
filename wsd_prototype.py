from nltk import wsd
import pandas as pd
import numpy as np
import nltk
import json
import torch
#nltk.download('averaged_perceptron_tagger')
#nltk.download('punkt')
#from nltk.corpus import wordnet as wn
#from spacy.cli import download
#from spacy import load
from flair.data import Sentence
from flair.embeddings import TransformerWordEmbeddings
#from pywsd.lesk import adapted_lesk
import torch
import warnings


def wsd_and_pos_prototype(sent, word, embedding_type='bert-base-uncased'):
    '''
    # WSD using Adapted Lesk's algorithm (Banerjee & Pederson) [gives more accurate results]
    synset = adapted_lesk(sent, word)

    # get embeddings for word and sentence using BERT (using flair library to do this)
    s=Sentence(sent)
    definition = Sentence(synset.definition())
    bert_embedding = TransformerWordEmbeddings('bert-base-uncased')
    bert_embedding.embed(s)
    bert_embedding.embed(definition)
    index = 0
    for token in s:
        if token.text == word:
            break
        index=index+1

    return synset.definition(), torch.stack([i.embedding for i in definition]), synset.pos(), s[index].embedding, torch.stack([i.embedding for i in s])
    '''
    # run the sentence through NLTK's POS tagger
    text = nltk.tokenize.word_tokenize(sent)
    poses = nltk.pos_tag(text)
    # get the word and POS from the tokenizer
    word,pos = [tup for tup in poses if tup[0]==word][0]
    # find the matching word and verb sense from the filtered MW definitions
    defs = pd.read_csv('./data_files/filtered_files/mw_words_filtered.csv')
    if 'JJ' in pos:
        pos='adjective'
    elif 'NN' in pos:
        pos='noun'
    elif 'RB' in pos:
        pos='adverb'
    elif 'VB' in pos:
        pos='verb'
    else:
        return 0,0,0,0
    definition = defs.loc[(defs['word'] == word) & (defs['pos'] == pos), 'dfns']
    if len(definition) == 0:
        return 0,0,0,0
    else:
        definition = definition.values[0]
    s=Sentence(sent)
    s_definition = Sentence(definition)
    bert_embedding = TransformerWordEmbeddings('bert-base-uncased')
    bert_embedding.embed(s)
    bert_embedding.embed(s_definition)
    index = 0
    for token in s:
        if token.text == word:
            break
        index=index+1
    return definition, torch.stack([i.embedding for i in s_definition]), s[index].embedding, torch.stack([i.embedding for i in s])

with open('proto.txt', 'r') as file:
    i=1
    data={}
    for line in file:
        sent,word = line.strip().split('::')
        dfn,e_dfn,e_wrd,e_sent = wsd_and_pos_prototype(sent,word)
        if dfn==0:
            print('definition not found')
            break
        if i>3: break
        input_tag, output_tag = 'input'+str(i), 'output'+str(i)
        data[input_tag]=line
        data[output_tag]={
            'definition':dfn,
            'definition_embedding':e_dfn.tolist(),
            'word_embedding':e_wrd.tolist(),
            'sentence_embedding':e_sent.tolist()
        }
        i+=1
    save_file = open('proto3.json','w')
    json.dump(data,save_file,indent=5)
    save_file.close()
