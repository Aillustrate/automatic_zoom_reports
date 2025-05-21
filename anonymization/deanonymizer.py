from abc import ABC, abstractmethod
from copy import deepcopy

from config import config
from anonymization.vllm_model import VLLMModel, remove_thinking
from summarization.summary import Summary
from anonymization.utils import compare_strings


class BaseDeanonymizer(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def insert_entities(self, texts, mapping):
        pass

    def deanonymize(self, summary:Summary, mapping):
        new_sections = {}
        for section_id, section in summary.sections.items():
                content = section["content"]
                print(content)
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
                new_sections[section_id] = {**section, "content": new_content}
        summary_dict = deepcopy(summary.to_dict())
        summary_dict["sections"] = new_sections
        return Summary.from_dict(summary_dict)


class RawDeanonymizer(BaseDeanonymizer):
    def __init__(self):
        super().__init__()

    def insert_entities(self, sentences, mapping):
        new_sentences = []
        for i, sentence in enumerate(sentences):
            new_sentence = sentence
            for key, value in mapping.items():
                new_sentence = new_sentence.replace(key, value)
            new_sentences.append(new_sentence)
        return new_sentences


class LLMDeanonymizer(BaseDeanonymizer):
    def __init__(self,
                 llm=None,
                 model=None,
                 tokenizer=None,
                 system_prompt_path=config.anonymization.llm_inserter_prompt_path,
                 **kwargs):
            super().__init__()
            if llm:
                    self.llm = llm
            else:
                with open(system_prompt_path, "r") as f:
                    system_prompt = f.read()
                self.llm = VLLMModel(model=model, tokenizer=tokenizer, system_prompt=system_prompt, **kwargs)


    def get_prompt(self, mapping, context):
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
        if self.use_llm:
            generated_insertions = self.llm.respond(prompts)
            generated_insertions = [remove_thinking(text) for text in generated_insertions]
            for i, replaced_sentence in zip(nums_sents_to_replace, generated_insertions):
                new_sentences[i] = replaced_sentence.split("\n")[0]
        return new_sentences