from automatic_zoom_reports.anonymization.anonymizer import Anonymizer
from automatic_zoom_reports.anonymization.entity_insertion import \
    BaseDeanonymizer
from automatic_zoom_reports.asr.transcription import Transcription
from automatic_zoom_reports.asr.transriber import Transcriber
from automatic_zoom_reports.summarization.summarizer import Summarizer
from automatic_zoom_reports.summarization.summary import Summary


class Pipeline:
    def __init__(
        self,
        transcriber: Transcriber,
        summarizer: Summarizer,
        anonymizer: Anonymizer,
        deanonymizer: BaseDeanonymizer
        ):
        self.transcriber = transcriber
        self.summarizer = summarizer
        self.anonymizer = anonymizer
        self.deanonymizer = deanonymizer

    def run(self, input_path: str, anonymize: bool = True):
        transcription = self.transcriber.transcribe(input_path)
        if anonymize:
            summary = self.get_summary_with_anonymization(transcription)
        else:
            summary = self.summarizer.summarize(transcription)
        return summary

    def get_summary_with_anonymization(self, transcription: Transcription):
        # get mapping and anonymized transcription
        mapping, anonymized_transcription = self.anonymizer.anonymize(transcription)
        # get summary from anonymized transcription
        anonymized_summary = self.summarizer.summarize(anonymized_transcription)
        # insert original entities into summary (deanonymize)
        summary = self.inserter.deanonymize(anonymized_summary, mapping)
        # set original (not anonymized) transcription
        summary.set_transcription(transcription)
        return summary

