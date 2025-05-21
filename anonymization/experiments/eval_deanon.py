import random
try:
    import pymorphy3
except ImportError:
    print("pymorphy3 not installed")
from copy import deepcopy


from anonymization.utils import split_punctuation, untokenize
from anonymization.entity_anonymization import compare_strings

random.seed(42)

def change_case(phrase, morph, case="nomn"):
    CASES = ["nomn", "gent", "datv", "accs", "ablt", "loct"]
    if case == "random":
        new_case = random.choice(CASES)
    else:
        new_case = case
        assert new_case in CASES, f"Invalid case: {new_case}"
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

def evaluate_entity_insertion(orig_texts, mapping, anonymized_texts, deanonymizer, case="original"):
    correct = 0
    total = 0
    new_mapping = deepcopy(mapping)
    if case != "original":
        assert "pymorphy3" in globals(), "pymorphy3 not installed"  # Check if pymorphy3 is installed
        morph = pymorphy3.MorphAnalyzer()
        for key, value in mapping.items():
            new_mapping[key] = change_case(value, morph, case=case) # "random" or "nomn"
    deanonymized_texts = deanonymizer.insert_entities(anonymized_texts, new_mapping)
    for i, (true, pred) in enumerate(zip(orig_texts, deanonymized_texts)):
        if compare_strings(true, pred):
            correct += 1
        else:
            print(f"{i}\tTrue: {true}\n\tPred: {pred}")
        total += 1
    return correct / total if total > 0 else 0.0