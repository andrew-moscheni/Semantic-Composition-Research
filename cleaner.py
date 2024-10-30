# import dependencies
import pandas as pd
import re
import os

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

    # remove unnecessary punctuation at the end of the file [ALL]
    df['dfn'] = df['dfn'].str.lstrip(' ').map(lambda s: s[-1] if s.endswith((':','.')) else s)
    # removes any instance that is just 'Also called' [free]
    df = df[df['dfn']!='Also called']
    # removes any instance of (= ) [Cambridge]
    df['dfn'] = df['dfn'].str.map(lambda s: re.sub(r'\(=\w+\)','',s))
    # removes one-word capitalized string list at beginning of a definition [Dict.com]
    df['dfn'] = df['dfn'].str.map(lambda s: re.sub(r'^ ([A-Z][a-zA-Z]*(, )?)+\.','',s))
    # remove sense ##, entry ##, (see ...) [MW words]
    df['dfn'] = df['dfn'].str.map(lambda s: re.sub(r'sense \d+|entry \d+|\(see [\w\s]+\)','',s))
    # Remove 'Compare ...' at the end of a definition after the definition [online API]
    df['dfn'] = df['dfn'].str.map(lambda s: re.sub(r'(?:[^.]*\.\s*)(Compare[^.]*\.)',r'\1',s))
    # removes empty instances from the dataframe [ALL]
    df = df[df['dfn']!='']

    # load the cleaned files into a separate directory
    df.to_csv(os.path.join(src_directory, filename), index=False)

print('All data files are cleaned!')
