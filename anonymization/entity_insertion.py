from copy import deepcopy

from anonymization.vllm_model import VLLMModel
from anonymization.anonymizer import Anonymizer

class LLMEntityInserter:
    def __init__(self,
                 llm=None,
                 logprobs=True,
                 model=None,
                 tokenizer=None,
                 system_prompt_path=None,
                 **kwargs):
        if llm:
            self.llm = llm
        else:
            with open(system_prompt_path, "r") as f:
                system_prompt = f.read()
            self.llm = VLLMModel(model=model, tokenizer=tokenizer, system_prompt=system_prompt, **kwargs)

    def get_prompt(self, phrase, context):
            return f"""ПРЕДЛОЖЕНИЕ: {context}
        ФРАЗА: {phrase}
        РЕЗУЛЬТАТ:"""


    def insert_entities(self, sentences, mapping):
        nums_sents_to_replace = []
        prompts = []
        for i, sentence in enumerate(sentences):
            for entity, phrase in mapping.items():
                if entity in sentence:
                    prompts.append(self.get_prompt(phrase, sentence))
                    nums_sents_to_replace.append(i)
        new_sentences = deepcopy(sentences)  # Create a deep copy to avoid modifying the original list
        generated_insertions = self.llm.respond(prompts)
        for i, replaced_sentence in zip(nums_sents_to_replace, generated_insertions):
            new_sentences[i] = replaced_sentence
        return new_sentences


def evaluate_entity_insertion(orig_texts, mapping, anonymized_texts, llm_entity_inserter, change=False):
    correct = 0
    total = 0
    new_mapping = deepcopy(mapping)
    if change:
        from anonymization.case_changing import change_case
        for key, value in mapping.items():
            new_mapping[key] = change_case(value)
    deanonymized_texts = llm_entity_inserter.insert_entities(anonymized_texts, new_mapping)
    for true, pred in zip(orig_texts, deanonymized_texts):
        if true == pred:
            correct += 1
        total += 1
    return correct / total if total > 0 else 0.0





