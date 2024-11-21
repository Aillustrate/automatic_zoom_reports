import json
import os

from openai import OpenAI

from config import config

class LLM:
    def __init__(self, system_prompt=None, 
                 system_prompt_file=None, 
                 model_name=config.llm.model):
        assert system_prompt or system_prompt_file, "Either system_prompt or system_prompt_path must be provided"
        if system_prompt_file:
            system_prompt_path = os.path.join(config.llm.prompts_dir, system_prompt_file)
            with open(system_prompt_path, "r") as f:
                system_prompt = f.read()
        with open(config.llm.token_usage_report_path, "r") as f:
            self.token_usage_report = json.load(f)
        self.system_prompt = system_prompt
        self.model_name = model_name
        self.client = OpenAI(api_key=config.auth.openai_api_key)
        
    
    def get_response(self, prompt):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}]
        )
        self.report_token_usage(response)
        completion = response.choices[0].message.content
        return completion
    
    def report_token_usage(self, response):
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        self.token_usage_report["total_prompt_tokens"] += prompt_tokens
        self.token_usage_report["total_completion_tokens"] += completion_tokens
        with open(config.llm.token_usage_report_path, "w") as f:
            json.dump(self.token_usage_report, f)
            
    def show_token_usage_report(self):
        prompt_tokens = self.token_usage_report["total_prompt_tokens"]
        completion_tokens = self.token_usage_report["total_completion_tokens"]
        print(f"Total prompt tokens: {prompt_tokens}")
        print(f"Total completion tokens: {completion_tokens}")
        print(f"Total tokens: {prompt_tokens + completion_tokens}")
        