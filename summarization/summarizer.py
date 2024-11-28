import datetime
import json
from typing import Any, Dict, List, Union

from asr.transcription import Transcription, load_transcription_and_transcript
from summarization.agents import (KeywordAgent, ShortSummaryAgent,
                                  StructuredSummaryAgent, TitleAgent)
from summarization.summary import Summary


class Summarizer:
    def __init__(self, token_usage_report_path):
        self.token_usage_report_path = token_usage_report_path
        self.init_agents()

    def init_agents(self):
        self.short_summary_agent = ShortSummaryAgent(self.token_usage_report_path)
        self.structured_summary_agent = StructuredSummaryAgent(
            self.token_usage_report_path
        )
        self.keyword_agent = KeywordAgent(self.token_usage_report_path)
        self.title_agent = TitleAgent(self.token_usage_report_path)

    def process_transcript(self, transcript: List[Dict[str, Any]]):
        dialog = "\n".join([f"{r['speaker']}: {r['text']}" for r in transcript])
        speakers = list(set([r["speaker"] for r in transcript]))
        return dialog, speakers

    def get_summary_data(self, transcript: List[Dict[str, Any]]):
        dialog, speakers = self.process_transcript(dialog)
        short_summary = self.short_summary_agent.reply(dialog)
        structured_summary = self.structured_summary_agent.reply(dialog)
        keywords = self.keyword_agent.reply(transcript)
        cur_datetime = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        summary_data = {
            "short_summary": short_summary,
            "structured_summary": structured_summary,
            "keywords": keywords,
            "date": cur_datetime,
            "speakers": speakers,
        }
        return summary_data

    def summarize(
        self,
        transcription: Union[Transcription, List[Dict[str, Any]], str],
        verbose=False,
    ):
        transcription, _ = load_transcription_and_transcript(transcription)
        dialog = transcription.to_str(include_timestamps=False)
        title = self.title_agent.reply(dialog)
        short_summary = self.short_summary_agent.reply(dialog)
        if verbose:
            print(f"Short summary: {short_summary}")
        structured_summary = self.structured_summary_agent.reply(dialog)
        if verbose:
            print(f"Structured summary: {structured_summary}")
        keywords = self.keyword_agent.reply(dialog)
        if verbose:
            print(f"Keywords: {keywords}")
        summary = Summary(
            title=title,
            short_summary=short_summary,
            structured_summary=structured_summary,
            keywords=keywords,
            transcription=transcription,
        )
        return summary


if __name__ == "__main__":
    summary = Summarizer("token_usage_report.json").summarize(
        Transcription.from_json("asr/results/transcription_merged.json")
    )
    print(summary)
