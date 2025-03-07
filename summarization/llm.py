import json
import os

from openai import OpenAI

from config import config


class LLM:
    def __init__(
        self,
        token_usage_report_path,
        model_name=config.llm.model,
    ):
        self.model_name = model_name
        self.client = OpenAI(api_key=config.auth.openai_api_key)
        self.token_usage_report_path = token_usage_report_path
        with open(self.token_usage_report_path, "r") as f:
            self.token_usage_report = json.load(f)
        if self.model_name not in self.token_usage_report:
            self.token_usage_report[self.model_name] = {
                "total_prompt_tokens": 0,
                "total_completion_tokens": 0,
            }

    def get_response(self, system_prompt, prompt):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        self.report_token_usage(response)
        completion = response.choices[0].message.content
        return completion

    def report_token_usage(self, response):
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        self.token_usage_report[self.model_name]["total_prompt_tokens"] += prompt_tokens
        self.token_usage_report[self.model_name][
            "total_completion_tokens"
        ] += completion_tokens
        with open(self.token_usage_report_path, "w") as f:
            json.dump(self.token_usage_report, f)

    def show_token_usage_report(self):
        prompt_tokens = self.token_usage_report[self.model_name]["total_prompt_tokens"]
        completion_tokens = self.token_usage_report[self.model_name][
            "total_completion_tokens"
        ]
        print(f"Total prompt tokens: {prompt_tokens}")
        print(f"Total completion tokens: {completion_tokens}")
        print(f"Total tokens: {prompt_tokens + completion_tokens}")
