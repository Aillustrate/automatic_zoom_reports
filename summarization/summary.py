import datetime
import json
from typing import Any, Dict, List, Optional, Union

from asr.transcription import Transcription, load_transcription_and_transcript
from summarization.output_validation import validate, validate_keywords, validate_structured_summary


class Summary:
    def __init__(self, short_summary, structured_summary, keywords, transcription:Union[Transcription, List[Dict[str, Any]], str]):
        self.short_summary = short_summary
        validate(structured_summary, validate_structured_summary)
        self.structured_summary = structured_summary
        validate(keywords, validate_keywords)
        self.keywords = keywords
        self.transcription, self.transcript = load_transcription_and_transcript(transcription)
        self._creation_date = Summary.init_creation_date()
    
    @staticmethod
    def init_creation_date():
        return datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        
    def get_creation_date(self):
        return self._creation_date
    
    def structured_summary_to_str(self):
        structured_summary = ""
        for topic, points in self.structured_summary.items():
            points_str = "\n".join([f"   - {point}" for point in points])
            structured_summary += f"{topic}:\n{points_str}\n"
        return structured_summary.strip()
    
    def structured_summary_to_html(self):
        structured_summary = ""
        for topic, points in self.structured_summary.items():
            points_str = "\n".join([f"<li>{point}</li>" for point in points])
            structured_summary += f"<b>{topic}:</b><ul>{points_str}</ul>"
        return structured_summary
    
    def to_dict(self, include_full_transcript:bool=True, transcript_format:str="dict"):
        if transcript_format == "html":
            speakers = self.transcription.get_speaker_ledgend()
        elif transcript_format == "str":
            speakers = ", ".join(self.transcription.speakers)
        else:
            speakers = self.transcription.speakers
        data = {
            "creation_date": self._creation_date,
            "keywords": self.keywords,
            "speakers": speakers,
            "short_summary": self.short_summary,
            "structured_summary": self.structured_summary,
        }
        if include_full_transcript:
            if transcript_format == "dict":
                data["transcript"] = self.transcript
            elif transcript_format == "html":
                data["transcript"] = self.transcription.to_html()
            elif transcript_format == "str":
                data["transcript"] = self.transcription.to_str()
        return data
    
    def to_str(self, include_full_transcript:bool=False):
        summary_template = """
        Дата: {self._creation_date}
        Участники: {speakers}
        Ключевые слова: {keywords}
        Супер краткое содержание\n{short_summary}\n
        Саммари по темам\n{structured_summary}
        """
        if include_full_transcript:
            summary_template += "\n\nРасшифровка\n{transcript}"
        summary = summary_template.format(**self.to_dict(include_full_transcript=include_full_transcript, transcript_format="str"))
        return summary
    
    def to_html(self, include_full_transcript:bool=False):
        summary_template = """
        <html>
        <meta charset="utf-8">
        <body>
        <b>Дата:</b> {self._creation_date}<br>
        <b>Участники:</b> {speakers}<br>
        <b>Ключевые слова:</b> {keywords}<br>
        <b>Супер краткое содержание:</b><br>{short_summary}<br><br>
        <b>Саммари по темам:</b><br>{structured_summary}
        """
        if include_full_transcript:
            summary_template += "<br><br><b>Расшифровка</b><br>{transcript}"
        summary_template += "</body></html>"
        summary = summary_template.format(**self.to_dict(include_full_transcript=include_full_transcript, transcript_format="html"))
        return summary
    
    def __repr__(self):
        return self.to_str(include_full_transcript=False)
        
    def save_json(self, output_path:str):
        assert output_path.endswith(".json"), "Output path must end with .json"
        with open(output_path, "w") as f:
            json.dump(self.to_dict(), f, indent=4)
        print(f"Summary saved to {output_path}")
    
    def save_txt(self, output_path:str):
        assert output_path.endswith(".txt"), "Output path must end with .txt"
        with open(output_path, "w") as f:
            f.write(self.to_str(include_full_transcript=True))
        print(f"Summary saved to {output_path}")
    
    def save_html(self, output_path:str):
        assert output_path.endswith(".html"), "Output path must end with .html"
        with open(output_path, "w") as f:
            f.write(self.to_str(include_full_transcript=True))
        print(f"Summary saved to {output_path}")
    
    @classmethod
    def from_dict(self, data):
        if "creation_date" not in data:
            data["creation_date"] = Summary.init_creation_date()
        return Summary(**data)

    @classmethod
    def from_json(self, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Summary.from_dict(data)
