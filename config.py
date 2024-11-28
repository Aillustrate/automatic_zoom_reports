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
    return config


config = get_config()
