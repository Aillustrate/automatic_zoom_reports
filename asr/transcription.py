import json
import random
from copy import deepcopy
from typing import Any, Dict, List, Tuple, Union


def merge_same_speakers(result: List[Tuple[float, float, str, str]])-> List[Tuple[float, float, str, str]]:
    """
    Merge consecutive segments with the same speaker.
    Example:
        SPEAKER_01 1.0 - 2.0: Привет!
        SPEAKER_01 2.0 - 3.0: Как дела?
        becomes
        SPEAKER_01 1.0 - 3.0: Привет! Как дела?
    """
    merged_result = []
    prev_speaker = None
    for start, end, text, speaker in result:
        if speaker == prev_speaker:
            merged_result[-1][2] += ' ' + text
            merged_result[-1][1] = end
        else:
            merged_result.append([start, end, text, speaker])
        prev_speaker = speaker
    return [tuple(r) for r in merged_result]


def align_transcripts_with_speakers(texts_with_timestamps: List[Tuple[float, float, str]], timestamps_speakers: List[Tuple[float, float, str]])-> List[Tuple[float, float, str, str]]:
    """
    Align speech recognition results with speaker diarization results based on timestamp overlap.
    """
    aligned_results = []

    for text_start, text_end, text in texts_with_timestamps:
        # Initialize variables to track the speaker(s) for this text segment
        segment_speakers = []
        total_overlap_duration = 0
        main_speaker = None
        max_overlap = 0

        # Find all speakers that overlap with this text segment
        for speaker_start, speaker_end, speaker in timestamps_speakers:
            # Calculate overlap between text and speaker segments
            overlap_start = max(text_start, speaker_start)
            overlap_end = min(text_end, speaker_end)

            if overlap_end > overlap_start:  # There is an overlap
                overlap_duration = overlap_end - overlap_start
                total_overlap_duration += overlap_duration

                # Keep track of speaker with maximum overlap
                if overlap_duration > max_overlap:
                    max_overlap = overlap_duration
                    main_speaker = speaker

                segment_speakers.append(
                    {"speaker": speaker, "overlap_duration": overlap_duration}
                )

        # If we found any overlapping speakers
        if main_speaker is not None:
            # Add the aligned result with the main speaker
            aligned_results.append((text_start, text_end, text, main_speaker))
        else:
            # If no speaker was found, mark as unknown
            aligned_results.append((text_start, text_end, text, "UNKNOWN_SPEAKER"))

    return merge_same_speakers(aligned_results)


class Transcription:
    def __init__(
        self,
        texts_with_timestamps: List[Tuple[float, float, str]],
        timestamps_speakers: List[Tuple[float, float, str]]
    ):
        self.COLORS = ["red", "green", "blue", "orange", "pink", "purple", "brown", "gray"]
        self.texts_with_timestamps = texts_with_timestamps
        self.timestamps_speakers = timestamps_speakers
        self.speakers = set([speaker for _, _, speaker in self.timestamps_speakers])
        self.speaker2color = self._get_color_mapping()
        self.result = align_transcripts_with_speakers(
                self.texts_with_timestamps, self.timestamps_speakers)

    def to_str(self, to_html=False, include_timestamps=True):
        lines = []
        for start, end, text, speaker in self.result:
            if to_html:
                color = self.speaker2color.get(speaker)
                speaker = f"<span style='color:{color}'>{speaker}</span>"
            if include_timestamps:
                lines.append(f"{speaker} {start} - {end}: {text}")
            else:
                lines.append(f"{speaker}: {text}")
        sep = "<br>" if to_html else "\n"
        return sep.join(lines)


    def to_html(self):
        speaker_legend = f"<b>Участники:</b> {self.get_speaker_ledgend()}"
        content = self.to_str(to_html=True)
        body = f"<body>{speaker_legend}<br>{content}</body>"
        doc = f'<html><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">{body}</html>'
        return doc

    def to_dict(self):
        return [
            {"start": start, "end": end, "text": text, "speaker": speaker}
            for start, end, text, speaker in self.result
        ]

    def _get_color_mapping(self):
        speaker2color = {}
        available_colors = deepcopy(self.COLORS)
        for speaker in self.speakers:
            if len(available_colors) == 0:
                available_colors = deepcopy(self.COLORS)
            color = random.choice(available_colors)
            speaker2color.update({speaker: color})
            available_colors.remove(color)
        return speaker2color

    def set_color_mapping(self, speaker2color):
        for speaker, color in speaker2color.items():
            self.speaker2color.update({speaker: color})

    def rename_speakers(self, name_mapping):
        timestamps_speakers = []
        for start, end, speaker in self.timestamps_speakers:
            speaker = name_mapping.get(speaker, speaker)
            timestamps_speakers.append((start, end, speaker))
        self.timestamps_speakers = timestamps_speakers
        self.speakers = set([speaker for _, _, speaker in self.timestamps_speakers])
        self.result = align_transcripts_with_speakers(
            self.texts_with_timestamps, self.timestamps_speakers
        )

        for old_speaker, new_speaker in name_mapping.items():
            if old_speaker in self.speaker2color:
                color = self.speaker2color.pop(old_speaker)
                self.speaker2color.update({new_speaker: color})
    
    def get_speaker_ledgend(self):
        legend = []
        for speaker in sorted(self.speakers):
            color = self.speaker2color.get(speaker)
            legend.append(f"<span style='color:{color}'>{speaker}</span>")
        return " ".join(legend)

    def __repr__(self):
        return self.to_str()

    def save_html(self, path="transcription.html"):
        assert path.endswith(".html"), "Path should end with .html"
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_html())
            print(f"Saved transcription to {path}")

    def save_txt(self, path="transcription.txt"):
        assert path.endswith(".txt"), "Path should end with .txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_str())
            print(f"Saved transcription to {path}")

    def save_json(self, path="transcription.json"):
        assert path.endswith(".json"), "Path should end with .json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)
            print(f"Saved transcription to {path}")
            
    @classmethod
    def from_dict(self, data):
        texts_with_timestamps = [(r["start"], r["end"], r["text"]) for r in data]
        timestamps_speakers = [(r["start"], r["end"], r["speaker"]) for r in data]
        return Transcription(texts_with_timestamps, timestamps_speakers)

    @classmethod
    def from_json(self, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Transcription.from_dict(data)

    
def load_transcription_and_transcript(obj:Union[Transcription, List[Dict[str, Any]], str]):
    if isinstance(obj, Transcription):
        return obj, obj.to_dict()
    elif isinstance(obj, list):
        return Transcription.from_dict(obj), obj
    elif isinstance(obj, str):
        if obj.endswith(".json"):
            return Transcription.from_json(obj), transcription.to_dict()
        else:
            raise ValueError("Path should end with .json")
    else:
        raise ValueError("Either transcription:Transcription, transcript:List[Dict[str, Any]] or transcript_path:str must be provided")
        


if __name__ == "__main__":
    transcription = Transcription.from_json("asr/results/transcription.json")
    print(transcription)
    transcription.save_html("asr/results/transcription_merged.html")
    transcription.save_txt("asr/results/transcription_merged.txt")
    transcription.save_json("asr/results/transcription_merged.json")
    transcription.rename_speakers({
        "SPEAKER_05": "ИВАН",
        "SPEAKER_03": "НАСТЯ",
        "SPEAKER_02": "САША",
        "SPEAKER_04": "ДМИТРИЙ",
        "SPEAKER_11": "АНТОН",
        "SPEAKER_08": "ВАЛЕНТИН"
        })
    print(transcription)
    print(transcription.get_speaker_ledgend())

    #print(merge_same_speakers(transcription.result))