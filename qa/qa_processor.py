import logging
from pathlib import Path
import sys
from typing import Union, Dict, Any

ROOT_DIR = str(Path(__file__).parent.parent)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from asr.transcription import Transcription, load_transcription_and_transcript
from llm_utils.llm import LLM

logging.basicConfig(level=logging.DEBUG)

class QAProcessor:
    SYSTEM_PROMPT = """
    Ты - ассистент, который помогает анализировать содержание встречи и отвечать на вопросы по нему.
    Твоя задача - внимательно проанализировать транскрипт встречи и дать точный и информативный ответ на заданный вопрос.
    Используй только информацию из транскрипта. Если в транскрипте нет информации для ответа на вопрос, так и скажи.
    Отвечай кратко и по существу.
    """

    def __init__(self, token_usage_report_path: str = "llm_utils/token_usage.json"):
        self.llm = LLM(token_usage_report_path)

    def process_transcript(self, transcript: list[Dict[str, Any]]):
        return "\n".join([f"{r['speaker']}: {r['text']}" for r in transcript])

    def answer_question(
        self,
        question: str,
        transcription: Union[Transcription, list[Dict[str, Any]], str],
        verbose: bool = False
    ) -> str:
        transcription, _ = load_transcription_and_transcript(transcription)
        dialog = transcription.to_str(include_timestamps=False)
        
        user_prompt = f"""
        Вопрос пользователя: {question}
        
        Транскрипт встречи:
        {dialog}
        
        Пожалуйста, проанализируй транскрипт встречи и дай точный ответ на этот вопрос.
        Если в транскрипте нет информации для ответа, напиши: "В транскрипте нет информации для ответа на этот вопрос."
        """
        
        response = self.llm.get_response(self.SYSTEM_PROMPT, user_prompt)
        
        if verbose:
            logging.info(f"Ответ на вопрос: {response}")
            
        return response


if __name__ == "__main__":
    # Пример использования
    qa_processor = QAProcessor()
    answer = qa_processor.answer_question(
        "Какие основные темы обсуждались на встрече?",
        Transcription.from_json("asr/results/transcription_merged.json")
    )
    print(answer) 