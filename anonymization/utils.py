import re
from string import punctuation

PAIRED_L2R = {'(': ')', '[': ']', '«': '»', '{': '}'}
PAIRED_R2L = dict(zip(PAIRED_L2R.values(), PAIRED_L2R.keys()))
UNPAIRED_PUNCT = ".,:;!?%^"
SYMM_QUOTES = ['"']

def hasproper(entity):
    tag_pattern = re.compile("</?[a-z]+>")
    entity = tag_pattern.sub("", entity).strip()
    for word in entity.split():
        if word[0].istitle():
            return True
        if word.startswith('"') or word.startswith("'") or word.startswith("«"):
            return True
    return False

def hasnum(entity):
    num_pattern = re.compile(r"\d+")
    if num_pattern.search(entity):
        return True
    return False

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

def remove_punctuation(text):
    for punct in punctuation:
        text = text.replace(punct, " ")
    text = re.sub("\s+", " ", text).strip()
    return text

def compare_strings(str1, str2):
    str1 = remove_punctuation(str1).lower().replace(" ", "").replace("\n", "")
    str2 = remove_punctuation(str2).lower().replace(" ", "").replace("\n", "")
    return str1 == str2