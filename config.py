import os

from dotenv import load_dotenv
from attrdict3 import AttrDict


def get_config() -> AttrDict:

    load_dotenv()
    config = AttrDict()

    config.auth = auth = AttrDict()
    config.auth.hf_token = os.environ.get("HF_TOKEN")

    config.asr = asr = AttrDict()
    config.asr.diarization_model = "pyannote/speaker-diarization-3.1"
    config.asr.language = "ru"


config = get_config()
