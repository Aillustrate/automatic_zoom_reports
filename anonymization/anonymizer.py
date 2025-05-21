import re
from copy import deepcopy
from typing import List, Optional, Union, Tuple, Dict
from collections import defaultdict

from anonymization.utils import untokenize
from anonymization.postprocess_ner import postprocess_preds
from anonymization.data_utils import bio2tag
from anonymization.entity_extractor import EntityExtractor
from anonymization.normalization import Normalizer
from anonymization.ner_validation import LLMValidator


class Anonymizer:
    """Class for text anonymization (NER + LLM validation)"""
    def __init__(self,
                 extractor: Optional[EntityExtractor] = None,
                 use_llm:bool=False,
                 validator: Optional[LLMValidator] = None,
                 do_normalize:bool=True):
        """
        Args:
            extractor (EntityExtractor, optional): Object for extracting entities from text uding NER model.
                If None (default), it will be initialized from scratch.
            use_llm (bool, optional): Whether to use LLM for validation. Defaults to False.
            validator (LLMValidator, optional): Object for validating anonymized entities using LLM.
                If None (default) and use_llm is True, it will be initialized from scratch.
            do_normalize (bool, optional): Whether to normalize the anonymized entities in the mapping.
        """
        if extractor is None:
            self.extractor = EntityExtractor()
        else:
            self.extractor = extractor

        self.use_llm = use_llm
        if validator is None and self.use_llm:
            self.validator = LLMValidator()
        else:
            self.validator = validator

        self.normalizer = Normalizer()
        self.do_normalize = do_normalize
        if self.do_normalize:
            self.normalizer.init_spacy()

    def mask(
        self,
        tokens: Union[List[str], List[List[str]]],
        labels: Union[List[str], List[List[str]]]
    )  -> Tuple[Dict[str, str], List[str]]:
        """Masks entities in the text and creates mapping of placeholder to original entity

        Args:
            tokens (Union[List[str], List[List[str]]]): Tokenized text(s). E.g. [["I", "work", "at", "Google"], ["Me", "too"]]
            labels (Union[List[str], List[List[str]]]): NER labels for each token. E.g. [["O", "O", "O", "ORG"], ["O", "O"]]

        Returns:
            Tuple[Dict[str, str], List[str]]: mapping and masked texts
                mapping (Dict[str, str]): Mapping from placeholder to original entity, e.g. {"[ORG_0]": "Google"}
                masked_texts (List[str]]): Masked texts, e.g. ["I work at [ORG_0]", "Me too"] where [ORG_0] is the anonymized entity
        """

        # if input contains only one text, wrap it in a list
        if not isinstance(tokens[0], list):
            tokens = [tokens]
            labels = [labels]

        entities = []
        tagged_sequences = []
        per_class_mapping = defaultdict(set)
        for ut_tokens, ut_labels in zip(tokens, labels):  # iterate over tokens and labels of each utterance
            tag_pattern = re.compile('</?[a-z]+>') # e.g. <org> or </org>
            entity_pattern = re.compile('<[a-z]+>.+?</[a-z]+>') # e.g. <org>Google</org>
            tagged_sequence = bio2tag(ut_tokens, ut_labels)  # convert BIO tags to <tag>entity</tag> format
            tagged_sequences.append(tagged_sequence)
            entities.extend(entity_pattern.findall(tagged_sequence)) # e.g. [<org>Google</org>, <person>John</person>]

        for entity in entities:
            entity_class = entity.split(">")[0].replace("<", "") # get entity class, e.g. org, person, address, money
            content = re.sub(tag_pattern, "", entity).strip() # get entity content, e.g. Google, John
            per_class_mapping[entity_class].add(content) # add entity to mapping, e.g. {org: {Google}, person: {John}}

        masked_texts = deepcopy(tagged_sequences)
        mapping = {}
        for entity_class, entities in per_class_mapping.items(): # e.g. (org, [Google, Apple])
            for i, entity in enumerate(entities): # e.g. (0, Google)
                # normalize entity if required, otherwise keep it as is
                norm_entity = self.normalizer.normalize(entity) if self.do_normalize else entity
                entity_mask = f"[{entity_class.upper()}_{i}]" # placeholder, e.g. [ORG_0] or [PERSON_1]
                mapping[entity_mask] = norm_entity  # e.g. {[ORG_0]: Google, [PERSON_1]: John}
                tagged_entity = f"<{entity_class}>{entity}</{entity_class}>" # e.g. <org>Google</org>
                # replace entity with mask in all tagged sequences, e.g. <org>Google</org> -> [ORG_0]
                for i in range(len(masked_texts)):
                    masked_texts[i] = masked_texts[i].replace(tagged_entity, entity_mask)

        return mapping, masked_texts

    # TODO: Devide this function into two: one for extracting entities and another for masking them
    def anonymize(self, texts: Union[str, List[str]], do_mask=True) -> Union[Tuple[Dict[str, str], List[str]], Tuple[List[str], List[str]]]:
        """_summary_

        Args:
            texts (Union[str, List[str]]): Text(s) to anonymize. E.g. "I work at Google" or ["I work at Google", "Me too"]
            do_mask (bool, optional): Whether to mask the entities in the text

        Returns:
            Union[Tuple[Dict[str, str], List[str]], Tuple[List[str], List[str]]]:
                If do_mask is True, returns a tuple of mapping and masked texts,
                    e.g. ({[ORG_0]: Google}, ["I work at [ORG_0]", "Me too"])
                If do_mask is False, returns a tuple of original tokens and predictions,
                    e.g. ([["I", "work", "at", "Google"], ["Me", "too"]], [["O", "O", "O", "ORG"], ["O", "O"]])
        """
        # if input contains only one text, wrap it in a list
        if isinstance(texts, str):
            texts = [texts]

        # get predictions
        all_preds = self.extractor.extract(texts) # list of [true_tokens, true_labels, pred_tokens, pred_labels]
        tokens = [p[2] for p in all_preds]
        predictions = [p[3] for p in all_preds]
        # postprocess predictions to remove overlapping entities
        predictions = [postprocess_preds(pred, tok) for pred, tok in zip(predictions, tokens)]

        # validate entities using LLM if required, otherwise keep predictions as is
        if self.use_llm:
            predictions = self.validator.validate_entities(tokens, predictions)

        # mask entities and create mappings
        if do_mask:
            return self.mask(tokens, predictions)
        return tokens, predictions


