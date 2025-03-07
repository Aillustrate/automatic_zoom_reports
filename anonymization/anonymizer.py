import re
from collections import defaultdict

from anonymization.tokenization_utils import untokenize
from anonymization.postprocess_ner import postprocess_preds
from anonymization.parse_dataset import bio2tag
from anonymization.bert_anonymizer import BertAnonymizer


def mask(tokens, labels):
    if not isinstance(tokens[0], list):
        tokens = [tokens]
        labels = [labels]

    entities = []
    tagged_sequences = []
    per_class_mapping = defaultdict(set)
    for ut_tokens, ut_labels in zip(tokens, labels):
        tag_pattern = re.compile('</?[a-z]+>')
        entity_pattern = re.compile('<[a-z]+>.+?</[a-z]+>')
        tagged_sequence = bio2tag(ut_tokens, ut_labels)
        tagged_sequences.append(tagged_sequence)
        entities.extend(entity_pattern.findall(tagged_sequence))

    for entity in entities:
        tag = entity.split(">")[0].replace("<", "")
        content = re.sub(tag_pattern, "", entity).strip()
        per_class_mapping[tag].add(content)

    mapping = {}
    for tag, entities in per_class_mapping.items():
        for i, entity in enumerate(entities):
            entity_mask = f"[{tag.upper()}_{i}]"
            mapping[entity_mask] = entity
            tagged_entity = f"<{tag}>{entity}</{tag}>"
            for i in range(len(tagged_sequences)):
                tagged_sequences[i] = tagged_sequences[i].replace(tagged_entity, entity_mask)

    return mapping, tagged_sequences



class Anonymizer:
    def __init__(self, bert=None, llm=None, use_llm=False):
        if bert is None:
            self.bert = BertAnonymizer()
        else:
            self.bert = bert
        if llm is None and use_llm:
            from anonymization.llm_validation import LLMValidator
            self.llm = LLMValidator()
        else:
            self.llm = llm

    def anonymize(self, texts, do_mask=True):
        if isinstance(texts, str):
            texts = [texts]

        all_preds = self.bert.anonymize(texts)
        tokens = [p[2] for p in all_preds]
        predictions = [p[3] for p in all_preds]
        predictions = [postprocess_preds(pred, tok) for pred, tok in zip(predictions, tokens)]

        if self.llm:
            predictions = self.llm.validate_entities(tokens, predictions)
        if do_mask:
            return mask(tokens, predictions)
        return tokens, predictions


