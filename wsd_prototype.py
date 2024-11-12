from nltk import wsd
import pandas as pd
import numpy as np
import nltk
from nltk.corpus import wordnet as wn
from spacy.cli import download
from spacy import load
import warnings

nltk.download('omw-1.4')
nltk.download('wordnet')
nltk.download('wordnet2022')
nlp = load('en_core_web_sm')

POS_MAP = {
    'VERB': wn.VERB,
    'NOUN': wn.NOUN,
    'PROPN': wn.NOUN
}


def wsd_and_pos_prototype(doc, word):
    found = False
    for token in doc:
        if token.text == word:
            word = token
            found = True
            break
    if not found:
        raise ValueError(f'Word \"{word}\" does not appear in the document: {doc.text}.')
    pos = POS_MAP.get(word.pos_, False)
    if not pos:
        warnings.warn(f'POS tag for {word.text} not found in wordnet. Falling back to default Lesk behaviour.')
    args = [c.text for c in doc], word.text
    kwargs = dict(pos=pos)
    return wsd.lesk(*args, **kwargs), pos


with open('proto.txt', 'r') as file:
    for line in file:
        sent,word = line.strip().split('::')
        synset,pos = wsd_and_pos_prototype(nlp(sent),word)
        print('SENT: {}'.format(sent))
        print('WORD: {}'.format(word))
        print('POS: {}'.format(pos))
        print('Dfn: {}'.format(synset.definition()))
        print('**********************************')