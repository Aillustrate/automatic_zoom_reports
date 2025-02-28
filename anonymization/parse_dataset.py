import re
from collections import defaultdict, Counter

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


def untokenize(tokens):
    text = " ".join(tokens)
    text = text.replace(" </", "</")
    text = re.sub("\s+", " ", text)
    text = text.strip()
    return text


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
