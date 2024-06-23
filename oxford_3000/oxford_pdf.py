'''
    This script generates the word list from the Oxford 3000 Dictionary word list. When creating it,
    just delete the first two lines since they are EMTPY. This script uses PyPDF2 to read each page
    from the PDF and extract its text, and the re package is useful in helping to extract the words from
    the list without the parts of speech or the A1/A2/B1/B2 information.
'''

# pip install PyPDF2

import PyPDF2
import re

reader_3000 = PyPDF2.PdfReader('./oxford_3000/oxford_3000.pdf')

i=0
with open('./oxford_3000/oxford_words.txt', 'w', encoding='utf-8') as file:
    for txt in reader_3000.pages:
        page = re.sub(r'(A1)|(A2)|(B1)|(B2)', '\n', txt.extract_text())
        for p in page.split('\n'):
            if p:
                splitted = p.split(' ')[0]
                if splitted not in [',', 'The']:
                    if splitted == '©':
                        splitted = p.split('™')[-1].split(' ')[0]
                    file.write(splitted+'\n')    
