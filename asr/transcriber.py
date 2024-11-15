import argparse
from asr.diarization import Diarizer
from asr.recognition import Recognizer
from asr.transcription import Transcription


class Transriber:
    def __init__(
        self,
        recognizer=None,
        diarizer=None,
        recognizer_model_dir=None,
        language="ru",
        diarizer_model="pyannote/speaker-diarization-3.1",
    ):
        if recognizer is None:
            self.recognizer = Recognizer(
                model_dir=recognizer_model_dir, language=language
            )
        else:
            self.recognizer = recognizer
        if diarizer is None:
            self.diarizer = Diarizer(model=diarizer_model)
        else:
            self.diarizer = diarizer

    def transcribe(self, input_path):
        texts_with_timestamps = self.recognizer.recognize(input_path)
        diarization = self.diarizer.diarize(input_path)
        return Transcription(texts_with_timestamps, diarization)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path", type=str, help="Path to input audio file")
    args = parser.parse_args()
    transriber = Transriber()
    transcription = transriber.transcribe(args.input_path)
    print(transcription)
