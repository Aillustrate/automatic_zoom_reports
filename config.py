import os

from dotenv import load_dotenv
from attrdict import AttrDict


def get_config() -> AttrDict:
    load_dotenv()
    config = AttrDict()

    config.auth = auth = AttrDict()
    auth.hf_token = os.environ.get("HF_TOKEN")

    config.asr = asr = AttrDict()
    asr.diarization_model = "pyannote/speaker-diarization-3.1"
    asr.language = "ru"
    return config

config = get_config()