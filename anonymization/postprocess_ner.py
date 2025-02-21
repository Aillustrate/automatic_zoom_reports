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


def test_fix_ner_annotations():
    # Sample input lists of tags and texts
    labels = [['O'], ['I-PERSON'], ['I-GPE', 'I-PERSON'], ['B-LOCATION'], ['B-LOCATION', 'B-CITY'], ['I-LOCATION'], ['O'], ['B-PERSON']]

    expected_output = ['O', 'B-PERSON', 'I-PERSON', 'B-LOCATION', 'I-LOCATION', 'I-LOCATION', 'O', 'B-PERSON']
    
    print(labels)

    # Run the function
    output = convert_labels(labels)
    print(output)

    # Check if the output matches the expected output
    assert output == expected_output, f"Expected {expected_output}, but got {output}"


if __name__ == "__main__":
    test_fix_ner_annotations()
