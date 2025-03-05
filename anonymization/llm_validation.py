from copy import deepcopy
from anonymization.parse_dataset import bio2tag, tag2bio
from anonymization.correct_labels import correct_labels
from anonymization.heuristic_validation import hasnum, hasproper
from anonymization.vllm_model import VLLMModel

def get_entity_positions(labels):
    labels = correct_labels(labels)  # Correct labels before processing
    if len(labels) == 0:
        return []
    positions = []
    prev_tag = "O"
    for i, label in enumerate(labels):
        tag = label.split("-")[-1]
        if tag != prev_tag and prev_tag != "O":
            positions[-1].append(i)
        if label.startswith("B-"):
            positions.append([i])
        prev_tag = tag
    if label != "O":
        positions[-1].append(i)
    return positions


def get_verdicts(logprobs, th = 0.5):
    verdicts = []
    for output_logprobs in logprobs:
        verdict = True
        for logprob in output_logprobs:
            if logprob.logprob > th:
                if logprob.decoded_token.strip().lower() == "no":
                    verdict = False
        verdicts.append(verdict)
    return verdicts



class LLMValidator:
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

        self.logprobs = logprobs


    def get_prompt(self, entity, context):
        if "<money>" in entity:
            prefix = "Reply YES if the entity contains a monetary amount or a large number, NO otherwise."
        if "<person>" in entity:
            prefix = "Reply YES if the entity contains a personal name (e.g., name, surname, or patronymic), NO otherwise."
        if "<address>" in entity:
            prefix = "Reply YES if the entity contains an address (e.g., city, district, street, or house number), NO otherwise."
        if "<org>" in entity:
            prefix = "Reply YES if the entity contains a company name or any proper noun, NO otherwise."
        else:
            prefix = "Reply YES if the entity contains confidential information or a proper noun, NO otherwise."

        prompt = f"""{prefix}
        CONTEXT: {context}
        ENTITY: {entity}
        ANSWER:"""
        return prompt

    def parse_responses(self, responses): #try logprobs
        verdicts = []
        for response in responses:
            if response.lower().startswith("no"):
                verdicts.append(False)
            else:
                verdicts.append(True)
        return verdicts

    def judge(self, entities, contexts):
        prompts = [
            self.get_prompt(entity, context)
            for ut_entities, context in zip(entities, contexts)
            for entity in ut_entities]
        if self.logprobs:
            logprobs = self.llm.get_logprobs(prompts)
            verdicts = get_verdicts(logprobs)
        else:
            responses = self.llm.respond(prompts)
            verdicts = self.parse_responses(responses)
        return verdicts

    def get_entities(self, tokens, labels):
        entities = []
        contexts = []
        entity_positions = []
        for i, (ut_tokens, ut_labels) in enumerate(zip(tokens, labels)):
            context = bio2tag(ut_tokens, ut_labels)
            contexts.append(context)
            entities.append([])
            positions = get_entity_positions(ut_labels)
            filtered_postitions = []
            if positions:
                for start, end in positions:
                    entity = bio2tag(ut_tokens[start:end], ut_labels[start:end])
                    if not hasproper(entity) and not hasnum(entity):
                        entities[-1].append((entity))
                        filtered_postitions.append((start, end))
            entity_positions.append(filtered_postitions)
        return entities, contexts, entity_positions


    def validate_entities(self, tokens, labels):
        entities, contexts, entity_positions = self.get_entities(tokens, labels)
        verdicts = self.judge(entities, contexts)
        print(verdicts)
        validated_labels = deepcopy(labels)
        n = 0
        for i, _ in enumerate(entity_positions):
            for j, (start, end) in enumerate(entity_positions[i]):
                verdict = verdicts[n]
                print(entities[i][j], verdict)
                if verdict is False:
                    for k in range(start, end):
                        validated_labels[i][k] = "O"
                n+=1

        return validated_labels



if __name__ == "__main__":
    text = "This is a <entity>test</entity> and another <entity>test</entity> and <entity>other</entity> and <org>other</org> and <org>other another</org> ."
    tokens, labels, entity_nums = tag2bio(text)
    validator = LLMValidator(None)
    print(validator.validate_entities([tokens], [labels]))

