from summarization.summary import Summary
from anonymization.utils import hasnum, hasproper
from anonymization.deanonymizer import RawDeanonymizer
from anonymization.postprocess_ner import correct_labels
from anonymization.ner_utils import tag2bio
from anonymization.ner_validation import BaseValidator


def test_validation():
    text = "This is a <entity>test</entity> and another <entity>test</entity> and <entity>other</entity> and <org>other</org> and <org>other another</org> ."
    expected_output = [['O', 'O', 'O', 'B-entity', 'O', 'O', 'B-entity', 'O', 'B-entity', 'O', 'B-org', 'O', 'B-org', 'I-org', 'O']]
    tokens, labels, entity_nums = tag2bio(text)
    validator = BaseValidator()
    assert validator.validate_entities([tokens], [labels]) == expected_output


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

def test_fix_ner_annotations():
    #labels = [['O'], ['I-PERSON'], ['I-GPE', 'I-PERSON'], ['B-LOCATION'], ['B-LOCATION', 'B-CITY'], ['I-LOCATION'], ['O'], ['B-PERSON']]
    labels = ['O', 'I-PERSON', 'I-PERSON', 'B-LOCATION', 'I-LOCATION', 'B-LOCATION', 'O', 'I-PERSON']
    expected_output = ['O', 'B-PERSON', 'I-PERSON', 'B-LOCATION', 'I-LOCATION', 'I-LOCATION', 'O', 'B-PERSON']
    output = correct_labels(labels)
    # Check if the output matches the expected output
    assert output == expected_output, f"Expected {expected_output}, but got {output}"

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