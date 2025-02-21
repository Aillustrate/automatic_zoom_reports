from collections import Counter, defaultdict

def parse_conll(file_path):
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
    tokens, labels = parse_conll("conll/all.conll")
    assert len(tokens) == len(labels)
    print(f'Total utterances: {len(tokens)}')
    for ut_tokens, ut_labels in zip(tokens, labels):
        assert len(ut_tokens) == len(ut_labels)
    print(count_labels(labels))
    print(count_label_tokens(count_labels(labels)))
    