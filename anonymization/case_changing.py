import random
import pymorphy3

from anonymization.tokenization_utils import split_punctuation, untokenize

morph = pymorphy3.MorphAnalyzer()

random.seed(42)


def change_case(phrase):
    CASES = ["nomn", "gent", "datv", "accs", "ablt", "loct"]
    new_case = random.choice(CASES)
    inflected_phrase = []
    for word in split_punctuation(phrase).split():
        parsed_word = morph.parse(word)[0]
        inflected_word = parsed_word.inflect({new_case})
        if inflected_word:
            inflected_word = inflected_word.word
            if word.istitle():
                inflected_word = inflected_word.capitalize()  # Capitalize the first letter if the original word was capitalized
            inflected_phrase.append(inflected_word)
        else:
            inflected_phrase.append(word)
    return untokenize(inflected_phrase)