from typing import List, Optional, Tuple, Union

import torch
from torch import nn
from tqdm.auto import trange
from transformers import AutoModelForTokenClassification, AutoTokenizer

from anonymization.utils import split_punctuation
from config import config


def load_model_and_tokenizer(model_name_or_path=config.anonymization.ner_model):
    model = AutoModelForTokenClassification.from_pretrained(model_name_or_path)
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
    return model, tokenizer

class EntityExtractor:
    """Class that extracts entities using a NER model"""
    def __init__(
            self,
            model: Optional[AutoModelForTokenClassification] = None,
            tokenizer: Optional[AutoTokenizer] = None,
            model_name_or_path: Optional[str] = config.anonymization.ner_model,
            device: Optional[Union[torch.device, str]] = None,
            ):
        """
        Args:
            model (AutoModelForTokenClassification, optional): NER model.
                If None, the model will be loaded using the model_name_or_path
            tokenizer (AutoTokenizer, optional): Tokenizer.
                If None, the tokenizer will be loaded using the model_name_or_path
            model_name_or_path (str, optional): Name or path of the model
            device (Union[torch.device, str], optional): Device to use for inference
        """
        self.device = device
        if self.device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.model_name_or_path = model_name_or_path
        if model is not None and tokenizer is not None:
            self.model, self.tokenizer = model, tokenizer
        else:
            self.model, self.tokenizer = load_model_and_tokenizer(self.model_name_or_path)
        self.model.to(self.device)
        self.model.eval()

    def predict(
        self,
        text:Union[List[str], str],
        output_together=True,
        glue_words=True
        ) -> Union[List[List[str]], Tuple[List[str], List[str]]]:
        """Get NER predictions for a given text
        Args:
            text (Union[List[str], str]): Text, either tokenized or not. E.g. ["I", "love", "New York"] or "I love New York"
            output_together (bool, optional): Whether to return the predictions for each token or the predictions for each word
                True: (["I", "love", "New York"], ["O", "O", "B-LOC"])
                False: [["I", "O"], ["love", "O"], ["New York", "B-LOC"]]
            glue_words (bool, optional): Whether to glue tokenized words together
                True: ["I", "love", "New York"]
                False: ["I", "love", "New", "York"]

        Returns:
            Union[List[List[str]], Tuple[List[str], List[str]]]: predictions
            If output_together is True,  (["I", "love", "New York"], [[O", "O", "B-LOC"])
            If output_together is False, [["I", "O"], ["love", "O"], ["New York", "B-LOC"]]
        """
        sigmoid = nn.Sigmoid()
        if isinstance(text, str):
            tokenized = self.tokenizer(text)
        else:
            tokenized = self.tokenizer("\t".join(text))
        input_ids = torch.tensor([tokenized["input_ids"]], dtype=torch.long).to(self.device)
        token_type_ids = torch.tensor([tokenized["token_type_ids"]], dtype=torch.long).to(self.device)
        attention_mask = torch.tensor([tokenized["attention_mask"]], dtype=torch.long).to(self.device)
        preds = self.model(**{"input_ids": input_ids, "token_type_ids": token_type_ids, "attention_mask": attention_mask})
        logits = sigmoid(preds.logits)

        output_tokens = []
        output_preds = []
        id_to_label = {int(k): v for k, v in self.model.config.id2label.items()}
        for i, token in enumerate(input_ids[0]):
            if token > 3:
                class_ids = (logits[0][i] > 0.5).nonzero()
                if class_ids.shape[0] >= 1:
                    class_names = [id_to_label[int(cl)] for cl in class_ids]
                else:
                    class_names = [id_to_label[int(logits[0][i].argmax())]]
                converted_token = self.tokenizer.convert_ids_to_tokens([token])[0]
                new_word_bool = converted_token.startswith("▁")
                converted_token = converted_token.replace("▁", "")
                if glue_words and not(new_word_bool) and output_tokens:
                    output_tokens[-1] += converted_token
                else:
                    output_tokens.append(converted_token)
                    output_preds.append(class_names[0])
            else:
                class_names = []
        del input_ids
        del token_type_ids
        del attention_mask
        if output_together:
            return [[output_tokens[t_i], output_preds[t_i]] for t_i in range(len(output_tokens))]
        return output_tokens, output_preds

    def extract(
        self,
        texts: Union[List[str], List[List[str]]],
        labels: Optional[List[List[str]]] = None,
        ) -> List[List[str]]:
        """Extracts entities from a list of texts
        Args:
            texts (Union[List[str], List[str[str]]]): A list of texts, either tokenized or not.
                E.g. [["I", "love", "New York"], ["Me", "too"]] or ["I love New York", "Me too"]
            labels (Optional[List[str[str]]], optional): A list of labels for each text. E.g. [["O", "O", "B-LOC"], ["O", "O"]]

        Returns:
            List[List[str]]: List of true_tokens, true_labels, pred_tokens, pred_labels
            true_tokens: input tokens
            true_labels: input labels (if provided)
            pred_tokens: predicted tokens (may differ from true_tokens because of tokenization)
            pred_labels: predicted labels
        """
        all_preds = []
        # use tqdm for multiple texts
        pbar = trange(len(texts)) if len(texts) > 1 else range(len(texts))
        for i in pbar:
            true_tokens = texts[i] # text, tokenized or not: ["I", "love", "New York"] or "I love New York"
            true_labels = labels[i] if labels is not None else None
            # if text is a string and labels is None, split the string into tokens
            if labels is None and isinstance(true_tokens, str):
                true_tokens = split_punctuation(true_tokens)
            # get predictions
            pred_tokens, pred_labels = self.predict(true_tokens, output_together=False, glue_words=True)
            # the model may predict multiple entities for the same token, so we take the first one
            # pred_labels = [ut_labels[0] for ut_labels in pred_labels]
            all_preds.append([true_tokens, true_labels, pred_tokens, pred_labels])
        return all_preds



