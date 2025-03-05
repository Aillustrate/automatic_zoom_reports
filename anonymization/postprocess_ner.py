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



def test_fix_ner_annotations():
    #labels = [['O'], ['I-PERSON'], ['I-GPE', 'I-PERSON'], ['B-LOCATION'], ['B-LOCATION', 'B-CITY'], ['I-LOCATION'], ['O'], ['B-PERSON']]

    labels = ['O', 'I-PERSON', 'I-PERSON', 'B-LOCATION', 'I-LOCATION', 'B-LOCATION', 'O', 'I-PERSON']
    expected_output = ['O', 'B-PERSON', 'I-PERSON', 'B-LOCATION', 'I-LOCATION', 'I-LOCATION', 'O', 'B-PERSON']

    print(labels)


    output = correct_labels(labels)
    print(output)

    # Check if the output matches the expected output
    assert output == expected_output, f"Expected {expected_output}, but got {output}"


if __name__ == "__main__":
    test_fix_ner_annotations()
