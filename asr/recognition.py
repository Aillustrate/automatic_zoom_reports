import argparse
import codecs
import logging
import os
import sys
import tempfile

sys.path.append("pisets")

import numpy as np
from pisets.asr.asr import (asr_logger, check_language,
                            initialize_model_for_speech_classification,
                            initialize_model_for_speech_recognition,
                            initialize_model_for_speech_segmentation,
                            transcribe)
from pisets.utils.utils import time_to_str
from pisets.wav_io.wav_io import (TARGET_SAMPLING_FREQUENCY, load_sound,
                                  transform_to_wavpcm)
from pydub import AudioSegment

from config import config

speech_to_srt_logger = logging.getLogger(__name__)


def transform_audio_to_wavpcm(audio_array: str, dst_fname: str) -> None:
    audio_array = (audio_array.astype(np.float32) - 128.0) / 128.0
    audio = AudioSegment(
        audio_array.tobytes(),
        frame_rate=16000,
        sample_width=audio_array.dtype.itemsize,
        channels=1,
    )
    print(audio)
    print(dst_fname)
    if audio.channels != 1:
        audio.set_channels(1)
    if audio.frame_rate != TARGET_SAMPLING_FREQUENCY:
        audio.set_frame_rate(TARGET_SAMPLING_FREQUENCY)
    if audio.frame_width != 2:
        audio.set_sample_width(2)
    target_parameters = [
        "-ac",
        "1",
        "-ar",
        f"{TARGET_SAMPLING_FREQUENCY}",
        "-acodec",
        "pcm_s16le",
    ]
    audio.export(dst_fname, format="wav", parameters=target_parameters)


def init_recognition_models(model_dir=None, language="ru"):
    language_name = check_language(language)
    if model_dir is None:
        wav2vec2_path = None
        audiotransformer_path = None
        whisper_path = None
    else:
        model_dir = os.path.normpath(model_dir)
        if not os.path.isdir(model_dir):
            err_msg = f'The directory "{model_dir}" does not exist!'
            speech_to_srt_logger.error(err_msg)
            raise IOError(err_msg)
        wav2vec2_path = os.path.join(model_dir, "wav2vec2")
        if not os.path.isdir(wav2vec2_path):
            err_msg = f'The directory "{wav2vec2_path}" does not exist!'
            speech_to_srt_logger.error(err_msg)
            raise IOError(err_msg)
        audiotransformer_path = os.path.join(model_dir, "ast")
        if not os.path.isdir(audiotransformer_path):
            err_msg = f'The directory "{audiotransformer_path}" does not exist!'
            speech_to_srt_logger.error(err_msg)
            raise IOError(err_msg)
        whisper_path = os.path.join(model_dir, "whisper")
        if not os.path.isdir(whisper_path):
            err_msg = f'The directory "{whisper_path}" does not exist!'
            speech_to_srt_logger.error(err_msg)
            raise IOError(err_msg)

    try:
        segmenter = initialize_model_for_speech_segmentation(
            language_name, model_info=wav2vec2_path
        )
    except BaseException as ex:
        err_msg = str(ex)
        speech_to_srt_logger.error(err_msg)
        raise
    speech_to_srt_logger.info("The Wav2Vec2-based segmenter is loaded.")

    try:
        vad = initialize_model_for_speech_classification(
            model_info=audiotransformer_path
        )
    except BaseException as ex:
        err_msg = str(ex)
        speech_to_srt_logger.error(err_msg)
        raise
    speech_to_srt_logger.info("The AST-based voice activity detector is loaded.")

    try:
        asr = initialize_model_for_speech_recognition(
            language_name, model_info=whisper_path
        )
    except BaseException as ex:
        err_msg = str(ex)
        speech_to_srt_logger.error(err_msg)
        raise
    speech_to_srt_logger.info("The Whisper-based ASR is initialized.")
    return segmenter, vad, asr


class Recognizer:
    def __init__(
        self,
        model_dir=None,
        language=config.asr.language,
        segmenter=None,
        vad=None,
        asr=None,
        **kwargs,
    ):
        if all((segmenter, vad, asr)):
            self.segmenter, self.vad, self.asr = segmenter, vad, asr
        else:
            self.segmenter, self.vad, self.asr = init_recognition_models(
                model_dir, language
            )

    def save_to_str(self, texts_with_timestamps, output_name, audio_fname):
        output_srt_fname = os.path.normpath(output_name)
        output_srt_dir = os.path.dirname(output_srt_fname)
        if len(output_srt_dir) > 0:
            if not os.path.isdir(output_srt_dir):
                err_msg = f'The directory "{output_srt_dir}" does not exist!'
                speech_to_srt_logger.error(err_msg)
                raise IOError(err_msg)
        if len(os.path.basename(output_srt_fname).strip()) == 0:
            err_msg = f'The file name "{output_srt_fname}" is incorrect!'
            speech_to_srt_logger.error(err_msg)
            raise IOError(err_msg)

        if os.path.basename(output_srt_fname) == os.path.basename(audio_fname):
            err_msg = (
                f"The input audio and the output SubRip file have the same names! "
                f"{os.path.basename(audio_fname)} = {os.path.basename(output_srt_fname)}"
            )
            speech_to_srt_logger.error(err_msg)
            raise IOError(err_msg)
            with codecs.open(output_srt_fname, mode="w", encoding="utf-8") as fp:
                for counter, (sent_start, sent_end, sentence_text) in enumerate(
                    texts_with_timestamps
                ):
                    fp.write(f"{counter + 1}\n")
                    fp.write(f"{time_to_str(sent_start)} --> {time_to_str(sent_end)}\n")
                    fp.write(f"{sentence_text}\n\n")

    def transform(self, audio_fname=None, audio=None):
        assert (audio is not None) or (
            audio_fname
        ), "Provide either audio or path to the file"
        tmp_wav_name = ""
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb", delete=False, suffix=".wav"
            ) as fp:
                tmp_wav_name = fp.name
                try:
                    if audio_fname:
                        transform_to_wavpcm(audio_fname, tmp_wav_name)
                        speech_to_srt_logger.info(
                            f'The sound "{audio_fname}" is converted to the "{tmp_wav_name}".'
                        )
                    elif audio is not None:
                        transform_audio_to_wavpcm(audio, tmp_wav_name)
                        speech_to_srt_logger.info(
                            f'The sound is converted to the "{tmp_wav_name}".'
                        )
                except BaseException as ex:
                    err_msg = str(ex)
                    speech_to_srt_logger.error(err_msg)
                    raise
            try:
                input_sound = load_sound(tmp_wav_name)
            except BaseException as ex:
                err_msg = str(ex)
                speech_to_srt_logger.error(err_msg)
                raise
            speech_to_srt_logger.info(f'The sound is "{tmp_wav_name}" is loaded.')
        except BaseException as ex:
            err_msg = str(ex)
            speech_to_srt_logger.error(err_msg)
            raise
        finally:
            if os.path.isfile(tmp_wav_name):
                #     os.remove(tmp_wav_name)
                speech_to_srt_logger.info(f'The sound is "{tmp_wav_name}" is removed.')
        return input_sound

    def recognize(self, input, from_file=True, output_name=None):
        if from_file:
            audio_fname = os.path.normpath(input)
            if not os.path.isfile(audio_fname):
                err_msg = f'The file "{audio_fname}" does not exist!'
                speech_to_srt_logger.error(err_msg)
                raise IOError(err_msg)
            input_sound = self.transform(audio_fname=audio_fname)
        else:
            audio_fname = None
            input_sound = self.transform(audio=input)

        if input_sound is None:
            speech_to_srt_logger.info(f"The sound is empty.")
            texts_with_timestamps = []
        else:
            if not isinstance(input_sound, np.ndarray):
                speech_to_srt_logger.info(f"The sound is stereo.")
                input_sound = (input_sound[0] + input_sound[1]) / 2.0
            speech_to_srt_logger.info(
                f"The total duration of the sound is "
                f"{time_to_str(input_sound.shape[0] / TARGET_SAMPLING_FREQUENCY)}."
            )

            texts_with_timestamps = transcribe(
                input_sound,
                self.segmenter,
                self.vad,
                self.asr,
                min_segment_size=1,
                max_segment_size=20,
            )

        if output_name:
            self.save_to_str(texts_with_timestamps, output_name, audio_fname)

        return texts_with_timestamps


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", type=str, help="Path to input audio file")
    args = parser.parse_args()
    recognizer = Recognizer()
    texts_with_timestamps = recognizer.recognize(args.input_path, from_file=True)
    print(texts_with_timestamps)
