from copy import deepcopy
from anonymization.parse_dataset import bio2tag, tag2bio
from anonymization.heuristic_validation import hasnum, hasproper

def get_entity_positions(labels):
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
    def __init__(self, llm, logprobs=True):
        self.llm = llm #add model init in validator init
        self.logprobs = logprobs
        

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
            entity_positions.append(positions)
            if positions:
                for start, end in positions:
                    entity = bio2tag(ut_tokens[start:end], ut_labels[start:end])
                    if not hasproper(entity) and not hasnum(entity):
                        entities[-1].append((entity))
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