import warnings

def entity_accuracy(predictions, ground_truth, strict=True):
    correct_entities = 0
    total_entities = 0

    for pred_sentence, true_sentence in zip(predictions, ground_truth):
        true_entities = set()
        pred_entities = set()

        # Collect true entities
        current_entity = []
        for true in true_sentence:
            if true != 'O':
                current_entity.append(true)
            else:
                if current_entity:
                    true_entities.add(tuple(current_entity))
                    current_entity = []
        if current_entity:
            true_entities.add(tuple(current_entity))

        # Collect predicted entities
        current_entity = []
        for pred in pred_sentence:
            if pred != 'O':
                current_entity.append(pred)
            else:
                if current_entity:
                    pred_entities.add(tuple(current_entity))
                    current_entity = []
        if current_entity:
            pred_entities.add(tuple(current_entity))

        if strict:
            correct_entities += len(true_entities.intersection(pred_entities))
        else:
            # Check for loose matches (any overlap)
            for true_entity in true_entities:
                for pred_entity in pred_entities:
                    if set(true_entity).intersection(set(pred_entity)):
                        correct_entities += 1
                        break

        total_entities += len(true_entities)

    return correct_entities / total_entities if total_entities > 0 else 0


def evaluate_ner(predictions, ground_truth):
    correct = 0
    total_predicted = 0
    total_actual = 0

    for i, (pred_sentence, true_sentence) in enumerate(zip(predictions, ground_truth)):
        if len(pred_sentence) != len(true_sentence):
            warnings.warn(f'Broken tokenization at sample {i}. " \
                          "Pred: {len(pred_sentence)}\t" \
                          "True:{len(true_sentence)}')
        for pred, true in zip(pred_sentence, true_sentence):
            if true != 'O':
                total_actual += 1
                if pred == true:
                    correct += 1
            if pred != 'O':
                total_predicted += 1

    accuracy = correct / total_predicted  if total_predicted > 0 else 0  # Calculate accuracy
    precision = correct / total_predicted if total_predicted > 0 else 0
    recall = correct / total_actual if total_actual > 0 else 0
    f1_score = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0
    
    loose_entity_accuracy = entity_accuracy(predictions, ground_truth, strict=False)
    strict_entity_accuracy = entity_accuracy(predictions, ground_truth, strict=True)

    return {
        'accuracy': accuracy,  # Added accuracy metric
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        "loose_entity_accuracy": loose_entity_accuracy,
        "strict_entity_accuracy": strict_entity_accuracy
    }
    
    
if __name__ == "__main__":
    gt = ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'I-MONEY', 'I-MONEY', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'B-PROFESSION', 'O', 'O', 'O', 'O', 'O', 'O', 'O']
    pred = ['O', 'O', 'O', 'O', 'O', 'O', 'B-MONEY', 'I-MONEY', 'I-MONEY', 'O', 'O', 'O', 'O', 'O', 'O', 'B-PROFESSION', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']
    print(evaluate_ner([pred], [gt]))