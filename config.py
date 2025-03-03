import os

from attrdict import AttrDict
from dotenv import load_dotenv


def get_config() -> AttrDict:
    load_dotenv()
    config = AttrDict()

    config.auth = auth = AttrDict()
    auth.hf_token = os.environ.get("HF_TOKEN")
    auth.openai_api_key = os.environ.get("OPENAI_API_KEY")
    config.asr = asr = AttrDict()
    asr.diarization_model = "pyannote/speaker-diarization-3.1"
    asr.language = "ru"

    config.llm = llm = AttrDict()
    llm.model = "gpt-4o-mini"
    llm.prompts_dir = "llm/prompts"
    llm.token_usage_report_path = "llm/token_usage.json"

    config.anonymization = anonymization = AttrDict()
    anonymization.model = "denis-gordeev/rured2-ner-microsoft-mdeberta-v3-base"
    anonymization.llm_validator_model = "Qwen/Qwen-2.5-0.5B-Instruct"
    anonymization.llm_validator_prompt_path = "anonymization/prompts/validation_prompt.txt"
    return config


config = get_config()
