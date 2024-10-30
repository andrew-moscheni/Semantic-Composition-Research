# import dependencies
import pandas as pd
import re
import os
from textblob import TextBlob

def clean_definition(definition):
    cleaned = definition
    # remove unnecessary punctuation at the end of the file [ALL]
    cleaned = s[-1] if s.endswith((':','.')) else s
    # removes any instance that is just 'Also called' [free]
    if cleaned == 'Also called':
        return ''
    # removes any instance of (= ) [Cambridge]
    cleaned =  re.sub(r'\(=\w+\)','',s)
    # removes one-word capitalized string list at beginning of a definition [Dict.com]
    cleaned = re.sub(r'^ ([A-Z][a-zA-Z]*(, )?)+\.','',s)
    # remove sense ##, entry ##, (see ...) [MW words]
    cleaned =  re.sub(r'sense \d+|entry \d+|\(see [\w\s]+\)','',s)
    # Remove 'Compare ...' at the end of a definition after the definition [online API]
    cleaned = re.sub(r'(?:[^.]*\.\s*)(Compare[^.]*\.)',r'\1',s)
    # remove unnececessary spaces from the beginning and end after substitution
    cleaned = cleaned.lstrip(' ').rstrip(' ')
    # now run every element through a spell checker
    blob = TextBlob(cleaned)
    cleaned = b.correct()

    # return the value once it has been cleaned and corrected
    return cleaned



# do a set of cleaning operations on ALL dictionaries to make cleaning more efficient
print('Cleaning data...')
# list out the src directory and the dst directory here
src_directory = './data_files/parsed_data_files'
dst_directory = './data_files/cleaned_files'
for filename in os.listdir(src_directory):
    # ALL files need to be cleaned of double-quoted strings
    df=pd.read_csv(os.path.join(src_directory, filename), quoting=csv.QUOTE_NONNUMERIC)

    # removes any word that has a comma in it (like A, a) [Cambridge]
    df = df[', ' not in df['word']]
    # ensures the word is not a prefix or a suffix
    df = df[not df['word'].endswith('-') or not df['word'].startswith('-')]

    # apply the function from above on all the definitions of the dataframe and streamline it to ensure
    # we are doing this efficiently
    df['dfn'] = df['dfn'].apply(clean_definition)

    # removes empty instances from the dataframe after the function is applied to each element
    df = df[df['dfn']!='']

    # load the cleaned files into a separate directory
    df.to_csv(os.path.join(src_directory, filename), index=False)

print('All data files are cleaned!')
