from copy import deepcopy

from config import config
from anonymization.vllm_model import VLLMModel, remove_thinking
from anonymization.anonymizer import Anonymizer
from anonymization.tokenization_utils import remove_punctuation
from summarization.summary import Summary
class LLMEntityInserter:
    def __init__(self,
                 llm=None,
                 logprobs=True,
                 model=None,
                 tokenizer=None,
                 system_prompt_path=config.anonymization.llm_inserter_prompt_path,
                 **kwargs):
        if llm:
            self.llm = llm
        else:
            with open(system_prompt_path, "r") as f:
                system_prompt = f.read()
            self.llm = VLLMModel(model=model, tokenizer=tokenizer, system_prompt=system_prompt, **kwargs)

    def get_prompt(self, mapping, context):
        # phrase_mapping = ", ".join([f"{k} - {v}" for k, v in mapping.items()])
        # return f"""CONTEXT: {context}
        # PHRASES: {phrase_mapping}
        # RESULT:"""
        for key, value in mapping.items():
            context = context.replace(key, f"[{value}]")
        prompt = f"""SENTENCE: {context}\nRESULT: """
        if "Qwen3" in str(self.llm.model_name_or_path):
            prompt += " /no_think"
        return prompt


    def insert_entities(self, sentences, mapping):
        nums_sents_to_replace = []
        prompts = []
        for i, sentence in enumerate(sentences):
            sentence_mapping = {k:v for k, v in mapping.items() if k in sentence}
            if len(sentence_mapping) > 0:  # Check if there are any entities to replace in the sentence
                nums_sents_to_replace.append(i)
                prompts.append(self.get_prompt(sentence_mapping, sentence))
        print(prompts[0])
        new_sentences = deepcopy(sentences)  # Create a deep copy to avoid modifying the original list
        generated_insertions = self.llm.respond(prompts)
        generated_insertions = [remove_thinking(text) for text in generated_insertions]
        for i, replaced_sentence in zip(nums_sents_to_replace, generated_insertions):
            new_sentences[i] = replaced_sentence.split("\n")[0]  # Take the first line of the generated text
        return new_sentences

    def deanonymize(self, summary:Summary, mapping):
        summary_dict = deepcopy(summary.to_dict())
        for section_id, content in summary_dict.items():
            if section_id not in ["creation_date", "speakers", "transcript"]:
                content = content["content"]
                if isinstance(content, list):
                    new_content = []
                    for element in content:
                        if isinstance(element, dict):
                            new_element = {}
                            assert "topic" in element and "points" in element
                            new_element["points"] = self.insert_entities(element["points"], mapping)
                            new_element["topic"] = self.insert_entities([element["topic"]], mapping)[0]
                        elif isinstance(element, str):
                            new_element = self.insert_entities([element], mapping)[0]
                        else:
                            raise ValueError(f"Unknown element type: {type(element)}")
                        new_content.append(new_element)
                elif isinstance(content, str):
                    new_content = self.insert_entities([content], mapping)[0]
                else:
                    raise ValueError(f"Unknown content type: {type(content)}")
                summary_dict[section_id]["content"] = new_content
        return Summary.from_dict(summary_dict)


def compare_strings(str1, str2):
    str1 = remove_punctuation(str1).lower().replace(" ", "").replace("\n", "")
    str2 = remove_punctuation(str2).lower().replace(" ", "").replace("\n", "")
    return str1 == str2


def evaluate_entity_insertion(orig_texts, mapping, anonymized_texts, llm_entity_inserter, case="original"):
    correct = 0
    total = 0
    new_mapping = deepcopy(mapping)
    if case != "original":
        from anonymization.case_changing import change_case
        for key, value in mapping.items():
            new_mapping[key] = change_case(value, case=case) # "random" or "nomn"
    deanonymized_texts = llm_entity_inserter.insert_entities(anonymized_texts, new_mapping)
    for i, (true, pred) in enumerate(zip(orig_texts, deanonymized_texts)):
        if compare_strings(true, pred):
            correct += 1
        else:
            print(f"{i}\tTrue: {true}\n\tPred: {pred}")
        total += 1
    return correct / total if total > 0 else 0.0





