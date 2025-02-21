import re
 
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
        text.append(f" <{tag.lower()}>")
    return untokenize(text)
            

if __name__ == "__main__":
    text = "This is a <entity>test</entity> and another <entity>test</entity> and <entity>other</entity> and <org>other</org> and <org>other another</org> ."
    tokens, labels, entity_nums = tag2bio(text)
    print("Tokens:", tokens)
    print("Labels:", labels)
    print("Entity Numbers:", entity_nums)
    print(bio2tag(tokens, labels))
    assert bio2tag(tokens, labels) == text