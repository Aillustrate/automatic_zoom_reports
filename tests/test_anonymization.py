from anonymization.utils import hasnum, hasproper

from summarization.summary import Summary
from anonymization.deanonymizer import RawDeanonymizer


def test_deanonymization():
    anonymized_summary = Summary.from_json("results/anon_summary.json")
    mapping = {
        "PERSON_1": "Настя",
        "PERSON_2": "Саша Мурзина",
        "ORG_1": "Звук",
        "ORG_2": "Positive Technologies",
        "MONEY_1": "1000 USD",
        "MONEY_1000": "1000000 USD",
        "ADDRESS_1": "123 Main St, Anytown, USA",
        "ADDRESS_2": "456 Elm St, Anytown, USA",
        }
    assert any(key in anonymized_summary.to_str() for key in mapping.keys())
    deanonymizer = RawDeanonymizer()
    deanonymized_summary = deanonymizer.deanonymize(anonymized_summary, mapping)
    assert all(mapping[key] in deanonymized_summary.to_str() for key in mapping.keys())

def test_hasnum():
    assert hasnum('23') == True
    assert hasnum('дом 15') == True
    assert hasnum('ООО "Пивозавр"') == False

def test_hasproper():
    assert hasproper("меня зовут Аня") == True
    assert hasproper("меня зовут аня") == False
    assert hasproper("my name is Ann") == True
    assert hasproper("<person>Аня") == True
    assert hasproper("<org>VK</org>") == True
    assert hasproper('ООО "Пивозавр"') == True
    assert hasproper("ООО 'Пивозавр") == True