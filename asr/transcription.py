import json
import random
from copy import deepcopy
from typing import List, Tuple


def align_transcripts_with_speakers(texts_with_timestamps, timestamps_speakers):
    """
    Align speech recognition results with speaker diarization results based on timestamp overlap.

    Args:
        texts_with_timestamps: List of tuples (start, end, text)
        timestamps_speakers: List of tuples (start, end, speaker)

    Returns:
        List of tuples (start, end, text, speaker)
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
            if aligned_results[-1][3] == main_speaker:
                text_start = aligned_results[-1][0]
                text = aligned_results[-1][2] + ' ' + text
                aligned_results.pop()
            aligned_results.append((text_start, text_end, text, main_speaker))
        else:
            # If no speaker was found, mark as unknown
            aligned_results.append((text_start, text_end, text, "UNKNOWN_SPEAKER"))

    return aligned_results


class Transcription:
    def __init__(
        self,
        texts_with_timestamps: List[Tuple[float, float, str]],
        timestamps_speakers: List[Tuple[float, float, str]],
    ):
        self.COLORS = ["red", "green", "blue", "orange", "pink"]
        self.texts_with_timestamps = texts_with_timestamps
        self.timestamps_speakers = timestamps_speakers
        self.speakers = set([speaker for _, _, speaker in self.timestamps_speakers])
        self.speaker2color = self._get_color_mapping()
        self.result = align_transcripts_with_speakers(
            self.texts_with_timestamps, self.timestamps_speakers
        )

    def to_str(self, to_html=False):
        lines = []
        for start, end, text, speaker in self.result:
            if to_html:
                color = self.speaker2color.get(speaker)
                speaker = f"<span style='color:{color}'>{speaker}</span>"
            lines.append(f"{speaker} {start} - {end}: {text}")
        sep = "<br>" if to_html else "\n"
        return sep.join(lines)


    def to_html(self):
        return self.to_str(to_html=True)

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
