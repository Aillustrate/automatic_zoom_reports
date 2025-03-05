import re
import warnings
from collections import defaultdict
import pandas as pd

from anonymization.llm_validation import get_entity_positions
from anonymization.parse_dataset import bio2tag

def entity_metrics(predictions, ground_truth, strict=True, format="pd"):
    correct_entities = 0
    total_true_entities = 0
    total_pred_entities = 0
    longer, shorter = 0, 0

    for pred_sentence, true_sentence in zip(predictions, ground_truth):
        true_entities = set()
        pred_entities = set()

        # Collect true entities
        current_entity = []
        for i, true in enumerate(true_sentence):
            if true != 'O':
                current_entity.append(i)
            else:
                if current_entity:
                    true_entities.add(frozenset(current_entity))
                    current_entity = []
        if current_entity:
            true_entities.add(frozenset(current_entity))

        # Collect predicted entities
        current_entity = []
        for i, pred in enumerate(pred_sentence):
            if pred != 'O':
                current_entity.append(i)
            else:
                if current_entity:
                    pred_entities.add(frozenset(current_entity))
                    current_entity = []
        if current_entity:
            pred_entities.add(frozenset(current_entity))

        if strict:
            correct_entities += len(true_entities.intersection(pred_entities))
        else:
            correct_entities += len(true_entities.intersection(pred_entities))
            for true_entity in true_entities:
                for pred_entity in pred_entities:
                    if true_entity != pred_entity:
                        if pred_entity > true_entity:
                            #print("rec", set(pred_entity), set(true_entity))
                            longer += 1
                            break
                        if pred_entity < true_entity:
                            #print("prec", set(pred_entity), set(true_entity))
                            shorter += 1
                            break

        total_true_entities += len(true_entities)
        total_pred_entities += len(pred_entities)

    precision = (correct_entities + shorter) / total_pred_entities if total_pred_entities > 0 else 0
    recall = (correct_entities + longer) / total_true_entities if total_true_entities > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    strictness = "strict" if strict else "loose"

    metrics = {
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
    }
    if format == "json":
        return metrics
    return pd.DataFrame({"score": {metric: score for metric, score in metrics.items()}})

def per_class_entity_metrics(predictions, ground_truth, strict=True, format="pd"):
    correct_entities = defaultdict(int)
    total_true_entities = defaultdict(int)
    total_pred_entities = defaultdict(int)
    false_negatives = defaultdict(list)

    for pred_sentence, true_sentence in zip(predictions, ground_truth):
        true_entities = set()
        pred_entities = set()

        # Collect true entities
        current_entity = []
        entity_type = None
        for true in true_sentence:
            if true != 'O':
                if entity_type is None:
                    entity_type = true.split('-')[-1]  # Extract entity type
                current_entity.append(true)
            else:
                if current_entity:
                    true_entities.add((tuple(current_entity), entity_type))
                    current_entity = []
                    entity_type = None
        if current_entity:
            true_entities.add((tuple(current_entity), entity_type))

        # Collect predicted entities
        current_entity = []
        entity_type = None
        for pred in pred_sentence:
            if pred != 'O':
                if entity_type is None:
                    entity_type = pred.split('-')[-1]  # Extract entity type
                current_entity.append(pred)
            else:
                if current_entity:
                    pred_entities.add((tuple(current_entity), entity_type))
                    current_entity = []
                    entity_type = None
        if current_entity:
            pred_entities.add((tuple(current_entity), entity_type))

        for entity, ent_type in true_entities:
            total_true_entities[ent_type] += 1
        for entity, ent_type in pred_entities:
            total_pred_entities[ent_type] += 1

        if strict:
            for entity, ent_type in true_entities.intersection(pred_entities):
                correct_entities[ent_type] += 1
        else:
            for true_entity, true_type in true_entities:
                for pred_entity, pred_type in pred_entities:
                    if true_type == pred_type and set(true_entity).intersection(set(pred_entity)):
                        correct_entities[true_type] += 1
                        break

        for entity, ent_type in true_entities - pred_entities:
            false_negatives[ent_type].append(entity)

    # Compute metrics per entity type
    per_class_metrics = {}
    for entity_type in set(total_true_entities.keys()).union(set(total_pred_entities.keys())):
        precision = correct_entities[entity_type] / total_pred_entities[entity_type] if total_pred_entities[entity_type] > 0 else 0
        recall = correct_entities[entity_type] / total_true_entities[entity_type] if total_true_entities[entity_type] > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        per_class_metrics[entity_type] = {'precision': precision, 'recall': recall, 'f1_score': f1_score}

    per_class_metrics = dict(sorted(per_class_metrics.items()))
    if format == "json":
        return per_class_metrics
    return pd.DataFrame(per_class_metrics)

def overall_token_metrics(predictions, ground_truth, format="pd"):
    correct_predicted = 0
    total_predicted = 0
    total_actual = 0
    correct = 0
    total = 0

    for i, (pred_sentence, true_sentence) in enumerate(zip(predictions, ground_truth)):
        if len(pred_sentence) != len(true_sentence):
            warnings.warn(f'Broken tokenization at sample {i}. " \
                          "Pred: {len(pred_sentence)}\t" \
                          "True:{len(true_sentence)}')
        for pred, true in zip(pred_sentence, true_sentence):
            if true != 'O':
                total_actual += 1
                if pred == true:
                    correct_predicted += 1
            if pred != 'O':
                total_predicted += 1
            if pred == true:
                correct += 1
            total += 1

    accuracy = correct / total # Calculate accuracy
    precision = correct_predicted / total_predicted if total_predicted > 0 else 0
    recall = correct_predicted / total_actual if total_actual > 0 else 0
    f1_score = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0

    metrics = {
        'accuracy': accuracy,  # Added accuracy metric
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score
    }
    if format == "json":
        return metrics
    return pd.DataFrame({"score": {metric: score for metric, score in metrics.items()}})

def per_class_token_metrics(predictions, ground_truth, strict=False, format="pd"):
    correct_tokens = defaultdict(int)
    total_true_tokens = defaultdict(int)
    total_pred_tokens = defaultdict(int)
    per_class_metrics = {}

    for i, (pred_sentence, true_sentence) in enumerate(zip(predictions, ground_truth)):
        for true_token, pred_token in zip(true_sentence, pred_sentence):
                true_type = true_token.split('-')[-1] if true_token != 'O' else 'O'
                pred_type = pred_token.split('-')[-1] if pred_token != 'O' else 'O'

                total_true_tokens[true_type] += 1
                total_pred_tokens[pred_type] += 1
                if true_token == pred_token:
                    correct_tokens[true_type] += 1
        for token_type in set(total_true_tokens.keys()).union(set(total_pred_tokens.keys())):
            if token_type != "O":
                precision = correct_tokens[token_type] / total_pred_tokens[token_type] if total_pred_tokens[token_type] > 0 else 0
                recall = correct_tokens[token_type] / total_true_tokens[token_type] if total_true_tokens[token_type] > 0 else 0
                f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                if token_type not in per_class_metrics:
                    per_class_metrics[token_type] = {}
                per_class_metrics[token_type].update({
                    'token_precision': precision,
                    'token_recall': recall,
                    'token_f1_score': f1_score
                })

    per_class_metrics = dict(sorted(per_class_metrics.items()))
    if format == "json":
        return per_class_metrics
    return pd.DataFrame(per_class_metrics)

def evaluate_ner(predictions, ground_truth, format="pd"):
    show = display if format == "pd" else print
    print("Overall per token metrics:")
    show(overall_token_metrics(predictions, ground_truth, format=format))
    print("\nLoose overall entity metrics:")
    show(entity_metrics(predictions, ground_truth, strict=False, format=format))
    print("\nStrict overall entity metrics:")
    show(entity_metrics(predictions, ground_truth, strict=True, format=format))
    print("\nPer class per token metrics:")
    show(per_class_token_metrics(predictions, ground_truth, format=format))
    print("\nLoose per class entity metrics:")
    show(per_class_entity_metrics(predictions, ground_truth, strict=False, format=format))
    print("\nStrict per class entity metrics:")
    show(per_class_entity_metrics(predictions, ground_truth, strict=True, format=format))


def show_false_negatives(predictions, ground_truth, tokens):
    all_false_negatives = []
    all_true_entities = []
    all_pred_entities = []
    for i, (pred_sentence, true_sentence, sentence) in enumerate(zip(predictions, ground_truth, tokens)):
            # Collect true entities
            true_entities = set()
            true_positions = get_entity_positions(true_sentence)
            for pos in true_positions:
                if len(pos) == 2:
                    start, end = pos
                    entity = bio2tag(sentence[start:end], true_sentence[start:end])
                    true_entities.add(entity)
            all_true_entities.append(true_entities)

            # Collect predicted entities
            pred_entities = set()
            pred_positions = get_entity_positions(pred_sentence)
            for pos in pred_positions:
                if len(pos) == 2:
                    start, end = pos
                    entity = bio2tag(sentence[start:end], pred_sentence[start:end])
                    pred_entities.add(entity)
            all_pred_entities.append(pred_entities)

            false_negatives = []
            for true_entity in true_entities:
                isfp = False
                if true_entity not in pred_entities:
                    for pred_entity in pred_entities:
                        tag_pattern = re.compile("</?[a-z]+>")
                        raw_true_entity = tag_pattern.sub("", true_entity)
                        raw_pred_entity = tag_pattern.sub("", pred_entity)
                        if raw_true_entity not in raw_pred_entity:
                            isfp = True
                if isfp:
                    false_negatives.append(true_entity)
            if len(false_negatives) > 0:
                all_false_negatives.append((i, false_negatives))

    for i, false_negatives in all_false_negatives:
            text = " ".join(tokens[i])
            print(f"Sample {i}: {text}")
            print(f"False Negatives: {false_negatives}")
            print(f"True: {all_true_entities[i]}")
            print(f"Pred: {all_pred_entities[i]}\n")

    return all_false_negatives



if __name__ == "__main__":
    gt = ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'I-MONEY', 'I-MONEY', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'B-PROFESSION', 'O', 'O', 'O', 'O', 'O', 'O', 'O']
    pred = ['O', 'O', 'O', 'O', 'O', 'O', 'B-MONEY', 'I-MONEY', 'I-MONEY', 'O', 'O', 'O', 'O', 'O', 'O', 'B-PROFESSION', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']
    print(overall_token_metrics([pred], [gt]))