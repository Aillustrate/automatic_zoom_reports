import argparse
from asr.diarization import Diarizer
from asr.recognition import Recognizer
from asr.transcription import Transcription
from asr.utils import extract_audio

from config import config


class Transriber:
    def __init__(
        self,
        recognizer=None,
        diarizer=None,
        recognizer_model_dir=None,
        language=config.asr.language,
        diarizer_model=config.asr.diarization_model
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

    def transcribe(self, input_path, from_video=True, verbose=True):
        VIDEO_FORMATS = ["mp4", "mkv", "avi"]
        AUDIO_FORMATS = ["wav", "mp3", "ogg", "flac"]
        if from_video and input_path.split(".")[-1] in VIDEO_FORMATS:
            if verbose:
                print("Extracting audio from video...")
            input_path = extract_audio(input_path)
        if verbose:
            print("Recognizing audio...")
        texts_with_timestamps = self.recognizer.recognize(input_path)
        if verbose:
            print("Identifying speakers...")
        diarization = self.diarizer.diarize(input_path)
        return Transcription(texts_with_timestamps, diarization)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", type=str, help="Path to input audio file")
    parser.add_argument("--from-video", action="store_true", help="Whether to transcribe from video or audio file")
    parser.add_argument("--verbose", action="store_true", help="Whether to print detailed logs")
    args = parser.parse_args()
    transriber = Transriber()
    transcription = transriber.transcribe(args.input_path, from_video=args.from_video, verbose=args.verbose)
    print(transcription)
