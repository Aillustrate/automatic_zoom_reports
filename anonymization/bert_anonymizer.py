from typing import List, Union
from tqdm.notebook import trange

import torch
from torch import nn
from transformers import AutoTokenizer, AutoModelForTokenClassification

from config import config

def load_model_and_tokenizer(model_name_or_path=config.anonymization.model):
    model = AutoModelForTokenClassification.from_pretrained(model_name_or_path).to(DEVICE)
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
    return model, tokenizer

class BertAnonymizer:
    def __init__(
            self,
            model=None,
            tokenizer=None,
            model_name_or_path=None,
            device=None
            ):
        self.device = device
        if self.device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_name_or_path = model_name_or_path
        if model is not None and tokenizer is not None:
            self.model, self.tokenizer = model, tokenizer
        else:
            self.model, self.tokenizer = load_model_and_tokenizer(self.model_name_or_path)
        self.model.eval()

    def predict(self, text:Union[List[str], str], glue_tokens=False, output_together=True, glue_words=True, device=DEVICE):
        sigmoid = nn.Sigmoid()
        if isinstance(text, str):
            tokenized = self.tokenizer(text)
        else:
            tokenized = self.tokenizer("\t".join(text))
        input_ids = torch.tensor([tokenized["input_ids"]], dtype=torch.long).to(device)
        token_type_ids = torch.tensor([tokenized["token_type_ids"]], dtype=torch.long).to(device)
        attention_mask = torch.tensor([tokenized["attention_mask"]], dtype=torch.long).to(device)
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
                    output_preds.append(class_names)
            else:
                class_names = []
        del input_ids
        del token_type_ids
        del attention_mask
        if output_together:
            return [[output_tokens[t_i], output_preds[t_i]] for t_i in range(len(output_tokens))]
        return output_tokens, output_preds

    def anonymize(self, tokens, labels):
        for i in trange(len(tokens)):
            true_tokens, true_labels = tokens[i], labels[i]
            pred_tokens, pred_labels = self.predict(true_tokens, output_together=False, glue_words=True)
            pred_labels = [ut_labels[0] for ut_labels in pred_labels]
            return true_tokens, true_labels, pred_tokens, pred_labels



