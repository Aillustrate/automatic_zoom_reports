import re
from collections import defaultdict

from anonymization.tokenization_utils import untokenize
from anonymization.postprocess_ner import postprocess_preds
from anonymization.parse_dataset import bio2tag

def mask(tokens, labels):
    text = []
    for token, label in zip(tokens, labels):
        if label.startswith("B-"):
            tag = label.split("-")[1]
            text.append(f"[{tag}]")
        elif label.startswith("I-"):
            continue
        else:
            text.append(token)
    return untokenize(text)


def mask(tokens, labels):
    per_class_mapping = defaultdict(set)
    tag_pattern = re.compile('</?[a-z]+>')
    entity_pattern = re.compile('<[a-z]+>.+?</[a-z]+>')
    tagged_sequence = bio2tag(tokens, labels)
    entities = entity_pattern.findall(tagged_sequence)
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
            tagged_sequence = re.sub(tagged_entity, entity_mask, tagged_sequence)

    return mapping, tagged_sequence







class Anonymizer:
    def __init__(self, bert, llm=None):
        self.bert = bert
        self.llm = llm

    def anonymize(self, texts, do_mask=True):
        all_preds = self.bert.anonymize(texts)
        tokens = [p[2] for p in all_preds]
        predictions = [p[3] for p in all_preds]
        predictions = [postprocess_preds(pred, tok) for pred, tok in zip(predictions, tokens)]

        if self.llm:
            predictions = self.llm.validate_entities(tokens, predictions)
        if do_mask:
            return [mask(tokens[i], predictions[i]) for i in range(len(tokens))]
        return tokens, predictions


