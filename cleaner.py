# import dependencies
import pandas as pd
import re
import os
import csv

from textblob import TextBlob


# function used in the apply method to streamline the code and avoid repetitive iterations through
# the dataframe
def clean_definition(definition):
    # removes any instance that is just 'Also called' [free]
    if  (pd.isna(definition)) or ('Also called' in definition):
        return ''
    # removes any instance of (= ) [Cambridge]
    cleaned = re.sub('\s*\(=\s*[^)]+\)','',definition)
    # removes one-word capitalized string list at beginning of a definition [Dict.com]
    # make sure we aren't removing definitions structured like that
    if cleaned.count('.') > 1:
        cleaned = re.sub(r'^\s*([A-Z][a-zA-Z]*,\s*)*[A-Z][a-zA-Z]*\.\s*','',cleaned)
    # remove sense ##, entry ##, (see ...) [MW words]
    cleaned =  re.sub(r'\ssense \d+|\sentry \d+|\s\(see [\w\s]+\)','',cleaned)
    # Remove 'Compare ...' at the end of a definition after the definition [online API]
    cleaned = re.sub(r'([^.]*\.\s*)(\(*[cC]ompare\s[^.]*\.*\)*)',r'\1',cleaned)
    # remove unnececessary spaces from the beginning and end after substitution
    cleaned = cleaned.lstrip(' ').rstrip(' ')
    # remove unnecessary punctuation at the end of the definition [ALL]
    cleaned = re.sub(r'[\.:]$', '', cleaned)
    # now run every element through a spell checker
    blob = TextBlob(cleaned)
    # typecast correction to turn it from a BaseBlob object into a String
    cleaned = str(blob.correct())

    # return the value once it has been cleaned and corrected
    return cleaned

# do a set of cleaning operations on ALL dictionaries to make cleaning more efficient
print('Cleaning data...')
# list out the src directory and the dst directory here
src_directory = './data_files/parsed_data_files'
dst_directory = './data_files/cleaned_files'
for filename in os.listdir(src_directory):
    # allow for retries to save time
    if os.path.exists(os.path.join(dst_directory, filename)):
        print(f'{filename} already exists!')
        continue

    # ALL files need to be cleaned of double-quoted strings
    df=pd.read_csv(os.path.join(src_directory, filename), quoting=csv.QUOTE_NONNUMERIC)

    # removes any word that has a comma in it (like A, a) [Cambridge]
    df=df[~df['word'].str.contains(', ')]
    # ensures the word is not a prefix or a suffix
    df = df[(~df['word'].str.endswith('-')) & (~df['word'].str.startswith('-'))]

    # apply the function from above on all the definitions of the dataframe and streamline it to ensure
    # we are doing this efficiently
    df['dfns'] = df['dfns'].apply(clean_definition)

    # removes empty instances from the dataframe after the function is applied to each element
    df = df[df['dfns']!='']

    # load the cleaned files into a separate directory
    df.to_csv(os.path.join(dst_directory, filename), index=False)
    print(f'Cleaned {filename}!')

print('All data files are cleaned!')
