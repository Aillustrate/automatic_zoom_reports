from abc import ABC, abstractmethod

from summarization.llm import LLM
from summarization.output_validation import (validate, validate_keywords,
                                             validate_structured_summary)
from summarization.parsing_utils import (parse_structured_summary,
                                         process_keywords)


class BaseAgent(ABC):
    def __init__(self, token_usage_report_path):
        self.system_prompt = self.get_system_prompt()
        self.llm = LLM(token_usage_report_path, self.system_prompt)

    @abstractmethod
    def get_system_prompt(self):
        pass

    def reply(self, text):
        return self.llm.get_response(text)


class TitleAgent(BaseAgent):
    def __init__(self, token_usage_report_path):
        super().__init__(token_usage_report_path)

    def get_system_prompt(self):
        return "Тебе дана расшифровка встречи. Сформулируй тему встречи во фразе из 1-7 слов. Например, 'Обсуждение стратегии развития'."


class ShortSummaryAgent(BaseAgent):
    def __init__(self, token_usage_report_path):
        super().__init__(token_usage_report_path)

    def get_system_prompt(self):
        return "Тебе дана расшифровка встречи. Опиши содержание встречи в 2-5 предложениях."


class StructuredSummaryAgent(BaseAgent):
    def __init__(self, token_usage_report_path):
        super().__init__(token_usage_report_path)

    def get_system_prompt(self):
        return """Тебе дана расшифровка встречи. Выдели от 1 до 7 тем, которые обсуждались на встрече и подпункты, обсуждавшиеся в каждой из тем.
Для каждой темы должно быть от 2 до 7 подпунктов. Верни результаты в формате json:
Пример выхода:
[
{"topic":"*тема 1*", "points":["*подпункт 1*", "*подпункт 2*"],
...}
]"""

    def reply(self, text):
        output = self.llm.get_response(text)
        structured_summary = parse_structured_summary(output)
        validate(structured_summary, validate_structured_summary)
        return structured_summary


class KeywordAgent(BaseAgent):
    def __init__(self, token_usage_report_path):
        super().__init__(token_usage_report_path)

    def get_system_prompt(self):
        return """Тебе дана расшифровка встречи. Выдели от 3 до 7 ключевых слов, относящихся ко встрече. Ключевые слова должны быть разделены запятой."""

    def reply(self, text):
        output = self.llm.get_response(text)
        keywords = process_keywords(output)
        validate(keywords, validate_keywords)
        return keywords
