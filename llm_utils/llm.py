import json
import logging
from pathlib import Path
from typing import Dict, Any

from openai import OpenAI

from config import config

logging.basicConfig(level=logging.DEBUG)

class LLM:
    def __init__(
        self,
        token_usage_report_path: str,
        model_name: str = config.llm.model,
    ):
        self.model_name = model_name
        self.client = OpenAI(api_key=config.auth.openai_api_key)
        self.token_usage_report_path = token_usage_report_path
        self.token_usage_report = self._load_token_usage()
        
        if self.model_name not in self.token_usage_report:
            self.token_usage_report[self.model_name] = {
                "total_prompt_tokens": 0,
                "total_completion_tokens": 0,
            }

    def _load_token_usage(self) -> Dict[str, Any]:
        try:
            with open(self.token_usage_report_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save_token_usage(self):
        with open(self.token_usage_report_path, "w") as f:
            json.dump(self.token_usage_report, f)

    def get_response(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]
            )

            self.report_token_usage(response)
            return response.choices[0].message.content

        except Exception as e:
            logging.error(f"Error in LLM response: {str(e)}")
            raise

    def report_token_usage(self, response):
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        self.token_usage_report[self.model_name]["total_prompt_tokens"] += prompt_tokens
        self.token_usage_report[self.model_name]["total_completion_tokens"] += completion_tokens
        self._save_token_usage()

    def show_token_usage_report(self):
        prompt_tokens = self.token_usage_report[self.model_name]["total_prompt_tokens"]
        completion_tokens = self.token_usage_report[self.model_name]["total_completion_tokens"]
        print(f"Total prompt tokens: {prompt_tokens}")
        print(f"Total completion tokens: {completion_tokens}")
        print(f"Total tokens: {prompt_tokens + completion_tokens}") 