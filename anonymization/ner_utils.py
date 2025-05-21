import json
import re
from collections import Counter, defaultdict

from anonymization.postprocess_ner import correct_labels
from anonymization.utils import untokenize


def get_entity_positions(labels):
    labels = correct_labels(labels)  # Correct labels before processing
    if len(labels) == 0:
        return []
    positions = []
    prev_tag = "O"
    for i, label in enumerate(labels):
        tag = label.split("-")[-1]
        if tag != prev_tag and prev_tag != "O":
            positions[-1].append(i)
        if label.startswith("B-"):
            positions.append([i])
        prev_tag = tag
    if label != "O":
        positions[-1].append(i)
    return positions


def remove_tags(text):
    tag_pattern = re.compile('</?[a-z]+>')
    text = tag_pattern.sub("", text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def parse_dialogs(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    dialogs = []
    for turns in data.values():
        turns = [remove_tags(turn) for turn in turns]
        turns = [f"- {utterance}" for utterance in turns]
        dialogue = "\n".join(turns)
        dialogs.append(dialogue)
    return dialogs


def tag2bio(text):
    import re

    # Dictionary to keep track of entity counts
    entity_count = {}
    # List to hold the tokens, BIO tags, and entity numbers
    tokens_list = []
    tags_list = []
    entity_numbers = []

    # Regular expression to find entities (supporting multi-word entities)
    pattern = re.compile(r'<(.*?)>(.*?)</\1>', re.DOTALL)

    # Initialize the position for the last index
    last_index = 0

    for match in pattern.finditer(text):
        entity_type = match.group(1)
        entity_value = match.group(2).strip()  # Remove leading/trailing whitespace
        # Update entity count for unique entity-value and type combinations
        entity_key = (entity_value, entity_type)
        if entity_key not in entity_count:
            entity_count[entity_key] = len(entity_count) + 1

        entity_id = entity_count[entity_key]

        # Add non-entity tokens as 'O'
        tokens = text[last_index:match.start()].split()
        for token in tokens:
            tokens_list.append(token)
            tags_list.append('O')
            entity_numbers.append(0)  # No entity number for non-entities

        # Add entity tokens
        entity_tokens = entity_value.split()  # Handle multi-word entities
        for i, token in enumerate(entity_tokens):
            if i == 0:
                tags_list.append(f'B-{entity_type}')
            else:
                tags_list.append(f'I-{entity_type}')
            tokens_list.append(token)
            entity_numbers.append(entity_id)  # Store the entity number

        # Update last index
        last_index = match.end()

    # Add remaining tokens as 'O'
    tokens = text[last_index:].split()
    for token in tokens:
        tokens_list.append(token)
        tags_list.append('O')
        entity_numbers.append(0)  # No entity number for non-entities

    return tokens_list, tags_list, entity_numbers


def correct_labels(prediction):
    prev_ents = ["O"]
    for i in range(len(prediction)):
        for j, tag in enumerate(prediction[i]):
            if tag.split('-')[-1] not in prev_ents:
                prediction[i][j] = prediction[i][j].replace('I-', 'B-')
            elif tag.split('-')[-1] in prev_ents:
                prediction[i][j] = prediction[i][j].replace('B-', 'I-')
        prev_ents = [tag.split('-')[-1] for tag in prediction[i]]
    return prediction

def delete_prepositions(tokens, labels):
    correct_labels = []
    PREPOSITIONS = ["на", "в", "около", "порядка", "до", "за"]
    for i, (token, label) in enumerate(zip(tokens, labels)):
        if token in PREPOSITIONS:
            if label.startswith('B-'):
                correct_labels.append(("O"))
            else:
                correct_labels.append((label))
        else:
            correct_labels.append((label))
    return correct_labels


def get_entity_tag(label):
    """Extract the entity tag (PERSON, LOCATION, etc.) from a label"""
    if label == 'O':
        return 'O'
    return label[2:] if label.startswith(('B-', 'I-')) else label

def convert_labels(labels):
    # Initialize result list
    result = []

    # Process each label group
    for i, label_group in enumerate(labels):
        # Get current label(s)
        current_labels = label_group

        # Rule 2: If entity starts with I- tag and it's the first label or
        # follows an O tag, convert to B-
        if i == 0 or (i > 0 and result[-1] == 'O'):
            current_labels = [l.replace('I-', 'B-') if l.startswith('I-') else l
                            for l in current_labels]

        # Rule 1: Handle label ambiguity
        chosen_label = current_labels[0]  # Default to first label

        if len(current_labels) > 1:  # If multiple labels
            if i > 0:
                prev_label = result[-1]
                prev_tag = get_entity_tag(prev_label)
                # Check if any current label's tag matches previous tag
                for label in current_labels:
                    if get_entity_tag(label) == prev_tag:
                        chosen_label = label
                        break

        # Rule 3: Handle consecutive entities of same class
        if i > 0:
            prev_label = result[-1]
            # Get entity tags (remove B- or I- prefix)
            curr_tag = get_entity_tag(chosen_label)
            prev_tag = get_entity_tag(prev_label)

            # If same entity type as previous and previous wasn't O
            if (chosen_label.startswith('B-') and
                curr_tag == prev_tag and
                prev_label != 'O'):
                # Convert current B- to I-
                chosen_label = 'I-' + curr_tag
        result.append(chosen_label)

    return result


def correct_labels(labels):
    correct_labels = []
    prev_tag = "O"
    for label in labels:
        tag = label.split("-")[-1]
        if tag != prev_tag and label.startswith("I-"):
            correct_labels.append(f"B-{tag}")
        elif tag == prev_tag and label.startswith("B-"):
            correct_labels.append(f"I-{tag}")
        else:
            correct_labels.append(label)
        prev_tag = tag
    return correct_labels

def apply_label_mapping(label):
    tag_mapping = {
        "ORGANIZATION": "ORG",
        "FAC": "ORG",
        "NEWS_SOURCE": "ORG",
        "CITY": "ADDRESS",
        "STREET": "ADDRESS",
        "VILLAGE": "ADDRESS",
        "REGION": "ADDRESS",
        "LOCATION": "ADDRESS",
        "BOROUGH": "ADDRESS",
        "HOUSE": "ADDRESS",
        "CARDINAL":"ADDRESS",
        "GPE": "ADDRESS",
        "PRICE": "MONEY",
        "INVESTMENT_PROGRAM": "MONEY",
        "PENALTY": "MONEY",
        "QUANTITY": "MONEY",
        "CURRENCY": "MONEY"
    }
    if label.startswith("B") or label.startswith("I"):
        index, tag = label.split('-')
        new_tag = tag_mapping.get(tag, tag)
        return f"{index}-{new_tag}"
    return label

def postprocess_preds(pred_labels, tokens, map_labels=True, remove_extra=True, remove_prepositions=True):
    allowed_tags = ["ORG", "PERSON", "ADDRESS", "MONEY", "O"]
    processed_labels = []
    for i, label in enumerate(pred_labels):
        new_label = apply_label_mapping(label) if map_labels else label
        if remove_extra and new_label.split('-')[-1] not in allowed_tags:
            new_label = "O"
        processed_labels.append(new_label)
    if remove_prepositions:
        processed_labels = delete_prepositions(tokens, processed_labels)
    processed_labels = correct_labels(processed_labels)
    return processed_labels


def bio2tag(tokens, labels):
    if len(tokens) == 0:
        return ""
    text = []
    prev_tag = "O"
    for token, label in zip(tokens, labels):
        tag = label.split("-")[-1]
        if tag != prev_tag and prev_tag != "O":
            text.append(f"</{prev_tag.lower()}>")
        if label.startswith("B-"):
            text.append(f" <{tag.lower()}>{token}")
        else:
            text.append(token)
        prev_tag = tag
    if label != "O":
        text.append(f"</{tag.lower()}>")
    return untokenize(text)



def conll2bio(file_path):
    tokens = [[]]  # Initialize with a nested list
    labels = [[]]  # Initialize with a nested list

    with open(file_path, 'r') as file:
        for line in file:
            if "DOCSTART" in line:
                continue
            if line.strip():  # Skip empty lines
                parts = line.split()
                tokens[-1].append(parts[0])  # Assuming the token is the first part
                labels[-1].append(parts[-1])  # Assuming the label is the last part
            else:
                tokens.append([])  # Start a new list for the next sentence
                labels.append([])  # Start a new list for the next sentence
    labels = [correct_labels(ut_labels) for ut_labels in labels]
    return tokens, labels


def count_labels(labels):
    flat_labels = [label for ut_labels in labels for label in ut_labels ]
    return Counter(flat_labels).most_common()

def count_label_tokens(bi_label_counts):
    total_label_tokens = defaultdict(int)
    for bi_label, counts in bi_label_counts:
        label = bi_label.split('-')[-1]
        total_label_tokens[label] += counts
    return total_label_tokens


if __name__ == "__main__":
    tokens, labels = conll2bio("conll/all.conll")
    assert len(tokens) == len(labels)
    print(f'Total utterances: {len(tokens)}')
    for ut_tokens, ut_labels in zip(tokens, labels):
        assert len(ut_tokens) == len(ut_labels)
    print(count_labels(labels))
    print(count_label_tokens(count_labels(labels)))


    text = "This is a <entity>test</entity> and another <entity>test</entity> and <entity>other</entity> and <org>other</org> and <org>other another</org> ."
    tokens, labels, entity_nums = tag2bio(text)
    print("Tokens:", tokens)
    print("Labels:", labels)
    print("Entity Numbers:", entity_nums)
    print(bio2tag(tokens, labels))
    assert bio2tag(tokens, labels) == text
