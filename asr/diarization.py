import argparse
import os
import torch
from pyannote.audio import Pipeline
from dotenv import load_dotenv
from config import config

load_dotenv()

def get_timestamps_speakers(diarization):
    diarization_timestamps = []
    for segment, _, label in diarization.itertracks(yield_label=True):
        diarization_timestamps.append((segment.start, segment.start + segment.duration, label))
    return diarization_timestamps

class Diarizer:
    def __init__(self, model=config.diarization_model, **kwargs):
        device = 'cuda' if torch.cuda.is_available else 'cpu'
        self.pipeline = Pipeline.from_pretrained(model,
  use_auth_token=os.environ['HF_TOKEN']).to(torch.device(device))

    def diarize(self, input_path, output_path=None):
        diarization = self.pipeline(input_path)
        if output_path:
            with open(output_path, "w") as rttm:
                diarization.write_rttm(rttm)
        return get_timestamps_speakers(diarization)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path", type=str, help="Path to input audio file")
    args = parser.parse_args()
    diarizer = Diarizer()
    timestamps_speakers = diarizer.diarize(args.input_path, from_file=True)
    print(timestamps_speakers)