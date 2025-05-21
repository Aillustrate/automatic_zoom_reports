from automatic_zoom_reports.asr.transriber import Transcriber
from automatic_zoom_reports.asr.transcription import Transcription
from automatic_zoom_reports.summarization.summarizer import Summarizer
from automatic_zoom_reports.summarization.summary import Summary

class Pipeline:
    def __init__(self, transcriber: Transcriber, summarizer: Summarizer, anonymizer: Anonymizer):
        self.transcriber = transcriber
        self.summarizer = summarizer
        self.anonymizer = anonymizer

    def run(self, input_path: str, output_path: str, anonymize: bool = True):
        transcription = self.transcriber.transcribe(input_path)
        if anonymize:
            mapping, anonymized_transcription = self.anonymizer.anonymize(transcription)
            anonymized_summary = self.summarizer.summarize(anonymized_transcription)

        else:
            summary = self.summarizer.summarize(transcription)
        return summary

    def save_summary(self, summary: Summary, output_path: str):
        with open(output_path, "w") as f: