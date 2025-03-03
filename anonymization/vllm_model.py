from vllm import SamplingParams, LLM
from transformers import AutoTokenizer


def load_vllm_and_tokenizer(model_name_or_path):
    model = LLM.load(model_name_or_path)
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
    return model, tokenizer

class VLLMModel:
    def __init__(
        self,
        system_prompt=None,
        model=None,
        tokenizer=None,
        model_name_or_path=None,
        **generation_params
    ):
        self.system_prompt = system_prompt
        self.model = model
        self.tokenizer = tokenizer
        self.generation_params = generation_params
        self.max_length = 2048
        self.model_name_or_path = model_name_or_path
        if model is not None and tokenizer is not None:
            self.model, self.tokenizer = model, tokenizer
        else:
            self.model, self.tokenizer = load_vllm_and_tokenizer(model_name_or_path)


    def get_prompt(self, text):
        return

    def get_prompt_tokens(self, texts, add_generation_prompt=True):
        messages_list = []
        for text in texts:
            if self.system_prompt is not None:
                messages = [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": text},
                ]
            else:
                messages = [{"role": "user", "content": text}]
            messages_list.append(messages)

        prompt_token_ids = [
            self.tokenizer.encode(
                self.tokenizer.apply_chat_template(messages, add_generation_prompt=add_generation_prompt, tokenize=False),
                add_special_tokens=True,
            )
            for messages in messages_list
        ]

        return prompt_token_ids


    def generate_answers(self, prompt_token_ids):
        sampling_params = SamplingParams(**self.generation_params, max_tokens=self.max_length)
        outputs = self.model.generate(prompt_token_ids=prompt_token_ids, sampling_params=sampling_params)
        generated_text = [output.outputs[0].text for output in outputs]
        return generated_text

    def get_logprobs(self, texts):
        single = False
        if isinstance(texts, str):
            single = True
            texts = [texts]
            print(single)
        prompt_token_ids = self.get_prompt_tokens(texts)
        sampling_params = SamplingParams(**self.generation_params, max_tokens=self.max_length, logprobs=True)
        outputs = self.model.generate(prompt_token_ids=prompt_token_ids, sampling_params=sampling_params)
        logprobs = [output.outputs[0].logprobs for output in outputs]
        return logprobs


    def respond(self, texts):
        single = False
        if isinstance(texts, str):
            single = True
            texts = [texts]
            print(single)
        prompt_tokens = self.get_prompt_tokens(texts)
        print(len(prompt_tokens))
        assistant_messages = self.generate_answers(prompt_tokens)
        if single:
            return assistant_messages[0]
        return assistant_messages