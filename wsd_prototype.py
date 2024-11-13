from nltk import wsd
import pandas as pd
import numpy as np
import nltk
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')
#from nltk.corpus import wordnet as wn
#from spacy.cli import download
#from spacy import load
from flair.data import Sentence
from flair.embeddings import TransformerWordEmbeddings
from pywsd.lesk import adapted_lesk
import torch
import warnings

'''
nltk.download('omw-1.4')
nltk.download('wordnet')
nltk.download('wordnet2022')
nlp = load('en_core_web_sm')

POS_MAP = {
    'VERB': wn.VERB,
    'NOUN': wn.NOUN,
    'PROPN': wn.NOUN
}
'''


def wsd_and_pos_prototype(sent, word):
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


with open('proto.txt', 'r') as file:
    for line in file:
        sent,word = line.strip().split('::')
        dfn,e_dfn,pos,e_wrd,e_sent = wsd_and_pos_prototype(sent,word)
        print('SENT: {}'.format(sent))
        print('WORD: {}'.format(word))
        print('POS: {}'.format(pos))
        print('Dfn: {}'.format(dfn))
        print('WORD EMBEDDING: {}'.format(e_wrd.shape))
        print('DEFINIITION EMBEDDING: {}'.format(e_dfn.shape))
        print('SENTENCE EMBEDDING: {}'.format(e_sent.shape))
        print('**********************************')
