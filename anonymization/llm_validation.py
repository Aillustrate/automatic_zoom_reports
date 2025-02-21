from copy import deepcopy
from parse_dataset import bio2tag, tag2bio

def get_entity_positions(labels):
    positions = []
    prev_tag = "O"
    for i, label in enumerate(labels):
        tag = label.split("-")[-1]
        if tag != prev_tag and prev_tag != "O":
            positions[-1].append(i)
        if label.startswith("B-"):
            positions.append([i])
        prev_tag = tag
    return positions


class LLMValidator:
    def __init__(self, llm):
        self.llm = llm #add model init in validator init
        

    def get_prompt(self, context, entity):
        return f"""
        Ответь YES, если сущность явялется конфиденциальной информацией и явялется именем собственным, NO - если сущность НЕ явялется конфиденциальной информацией или не является именем собственным.
        КОНТЕКСТ: {context}
        СУЩНОСТЬ: {entity}
        ОТВЕТ:"""
    
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
            for entity, context in zip(entities, contexts)]
        print(entities)
        responses = self.llm.generate_answer(prompts)
        verdicts = self.parse_responses(responses)
        return [["test" not in entity for ut_entities in entities for entity in ut_entities]]
    
    def validate_entities(self, tokens, labels):
        entities = []
        contexts = []
        entity_positions = []
        for i, (ut_tokens, ut_labels) in enumerate(zip(tokens, labels)):
            context = bio2tag(ut_tokens, ut_labels)
            contexts.append(context)
            entities.append([])
            positions = get_entity_positions(ut_labels)
            entity_positions.append(positions)
            for start, end in positions:
                entity = bio2tag(ut_tokens[start:end], ut_labels[start:end])
                entities[-1].append((entity))
        verdicts = self.judge(entities, contexts)
        print(verdicts)
        validated_labels = deepcopy(labels)
        for i, ut_verdicts in enumerate(verdicts):
            for j, verdict in enumerate(ut_verdicts):
                if verdict is False:
                    start, end = entity_positions[i][j]
                    for j in range(start, end):
                        validated_labels[i][j] = "O"
        return validated_labels



if __name__ == "__main__":
    text = "This is a <entity>test</entity> and another <entity>test</entity> and <entity>other</entity> and <org>other</org> and <org>other another</org> ."
    tokens, labels, entity_nums = tag2bio(text)
    validator = LLMValidator(None)
    print(validator.validate_entities([tokens], [labels]))