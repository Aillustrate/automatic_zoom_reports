import re

PAIRED_L2R = {'(': ')', '[': ']', '«': '»', '{': '}'}
PAIRED_R2L = dict(zip(PAIRED_L2R.values(), PAIRED_L2R.keys()))
UNPAIRED_PUNCT = ".,:;!?%^"
SYMM_QUOTES = ['"']

def untokenize(tokens) -> str:
    untokenized_text = []
    sep = ''
    for token in tokens:
        if token in UNPAIRED_PUNCT or token in PAIRED_R2L:
            untokenized_text.append(token)
        else:
            untokenized_text.append(sep + token)
            sep = ' '
            if token in PAIRED_L2R:
                sep = ''
    text = ''.join(untokenized_text)
    text = text.replace(" </", "</")
    text = re.sub("\s+", " ", text)
    text = text.strip()
    return text

def split_punctuation(text):
    for punct in UNPAIRED_PUNCT:
        text = text.replace(punct, f" {punct} ")
    text = re.sub("\s+", " ", text).strip()
    return text