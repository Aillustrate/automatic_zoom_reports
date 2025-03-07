import logging
from pathlib import Path
import sys
import datetime
import json
from typing import Any, Dict, List, Optional, Union

ROOT_DIR = str(Path(__file__).parent.parent)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from asr.transcription import Transcription, load_transcription_and_transcript

logging.basicConfig(level=logging.DEBUG)

class Summary:
    def __init__(
        self,
        sections: Dict[str, Any],
        transcription: Union[Transcription, List[Dict[str, Any]], str],
    ):
        """
        Args:
            sections: Словарь с секциями отчета, где ключ - id секции, значение - содержание
            transcription: Транскрипция встречи
        """
        self.sections = sections
        self.transcription, self.transcript = load_transcription_and_transcript(
            transcription
        )
        self._creation_date = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    def json_structure_to_str(self, structure_content):
        structure_content_str = ""
        for topic in structure_content:
            if isinstance(topic["points"], list):
                points_str = "\n".join([f"   - {point}" for point in topic["points"]])
            else:
                points_str = topic['points']
            structure_content_str += f"{topic['topic']}:\n{points_str}\n"
        return structure_content_str.strip()

    def json_structure_to_html(self, structure_content):
        structure_content_html = ""
        for topic in structure_content:
            if isinstance(topic["points"], list):
                points_str = "\n".join([f"<li>{point}</li>" for point in topic["points"]])
            else:
                points_str = topic['points']
            structure_content_html += f"<br><b>{topic['topic']}:</b><ul>{points_str}</ul>"
        return structure_content_html

    def to_dict(self, include_full_transcript: bool = True, transcript_format: str = "dict") -> Dict:
        data = {}
        data['creation_date']= self._creation_date
        if transcript_format == "html":
            data['speakers'] = self.transcription.get_speaker_ledgend()
            for section_id, content in self.sections.items():
                if content['type'] == 'json':
                    data[section_id] = self.json_structure_to_html(content['content'])
                elif content['type'] == 'list':
                    data[section_id] = ", ".join(content['content'])
                else:
                    data[section_id] = content['content']
        elif transcript_format == "str":
            data['speakers'] = ", ".join(self.transcription.speakers)
            for section_id, content in self.sections.items():
                if content['type'] == 'json':
                    data[section_id] = self.json_structure_to_str(content['content'])
                elif content['type'] == 'list':
                    data[section_id] = ", ".join(content['content'])
                else:
                    data[section_id] = content['content']
        else:
            data['speakers'] = self.transcription.speakers
            for section_id, content in self.sections.items():
                data[section_id] = content['content']

        if include_full_transcript:
            if transcript_format == "dict":
                data["transcript"] = self.transcript
            elif transcript_format == "html":
                data["transcript"] = self.transcription.to_html()
            elif transcript_format == "str":
                data["transcript"] = self.transcription.to_str()

        return data

    def to_str(self, include_full_transcript: bool = False) -> str:
        summary_template = "{title}\nДата: {creation_date}\nУчастники: {speakers}"

        for section_id, content in self.sections.items():
            header = content['name']
            summary_template += f"\n\n{header}:\n{{{section_id}}}\n"

        if include_full_transcript:
            summary_template += "\n\nРасшифровка\n{transcript}"
        format_args = self.to_dict(
            include_full_transcript=include_full_transcript, transcript_format="str"
        )
        summary = summary_template.format(**format_args)
        return summary

    def to_html(self, include_full_transcript: bool = False):
        summary_template = """
        <html>
        <meta charset="utf-8">
        <body>
        <h1>{title}</h1>
        <b>Дата:</b> {creation_date}<br>
        <b>Участники:</b> {speakers}<br>
        """
        
        for section_id, content in self.sections.items():
            header = content['name']
            summary_template += f'<br><br><b>{header}:</b><br>{{{section_id}}}'

        if include_full_transcript:
            summary_template += "<br><br><b>Расшифровка</b><br>{transcript}"
        
        summary_template += "</body></html>"
        format_args = self.to_dict(
            include_full_transcript=include_full_transcript, transcript_format="html"
        )
        summary = summary_template.format(**format_args)
        return summary

    def __repr__(self):
        return self.to_str(include_full_transcript=False)

    def save_json(self, output_path: str = "summary.txt"):
        assert output_path.endswith(".json"), "Output path must end with .json"
        with open(output_path, "w") as f:
            json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)
        logging.info(f"Summary saved to {output_path}")

    def save_txt(self, output_path: str = "summary.txt"):
        assert output_path.endswith(".txt"), "Output path must end with .txt"
        with open(output_path, "w") as f:
            f.write(self.to_str(include_full_transcript=True))
        logging.info(f"Summary saved to {output_path}")

    def save_html(self, output_path: str = "summary.txt"):
        assert output_path.endswith(".html"), "Output path must end with .html"
        with open(output_path, "w") as f:
            f.write(self.to_html(include_full_transcript=True))
        logging.info(f"Summary saved to {output_path}")

    # TODO: подумать нужна ли вообще эта ф-я
    @classmethod
    def from_dict(cls, data):
        # summary_data = {
        #     'transcription': data['transcript'],
        #     'sections': {}
        # }
        # for key in data:
        #     if key == 'transcription':
        #         summary_data['transcription'] = data[key]
        #     if key not in ['creation_data', 'speakers']:
        #         summary_data['sections'][key] = data[key]
        # return cls(**summary_data)
        return cls(**data)

    @classmethod
    def from_json(cls, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)


if __name__ == "__main__":
    sections = {
        "title": {
            "name": "Название встречи",
            "content": "Карьерная дискуссия",
            "type": "string"
        },
        "keywords": {
            "name": "Ключевые слова",
            "content": [
                "карьера",
                "машинное обучение",
                "бизнес-задачи",
                "большие данные",
                "стартапы",
                "хакерские атаки",
                "мероприятия",
            ],
            "type": "list"
        },
        "short_summary": {
            "name": "Супер краткое содержание",
            "content": "На встрече участники представили себя и обсудили свои карьерные пути в области машинного обучения и бизнес-анализа. Настя поделилась своим опытом работы в различных компаниях и стартапах, а также своей текущей деятельностью в компании «Звук»",
            "type": "string"
        },
        "structured_summary": {
            "name": "Краткое содержание по темам",
            "content": [
                {
                    "topic": "Представление участников",
                    "points": [
                        "Настя рассказывает о своем опыте работы в сфере NLP и бизнес-задачах.",
                        "Саша Мурзина делится своей ролью в компании Positive Technologies и их важности.",
                        "Дмитрий Колодьев упоминает свою работу в промсофте и участие в УДС 'Сайбирия'.",
                        "Каждый участник кратко представляется и делится своим опытом.",
                    ],
                },
                {
                    "topic": "Опыт в машинном обучении",
                    "points": [
                        "Настя обсуждает свой опыт работы с бигдатой и машинным обучением.",
                        "Саша делится своими обязанностями и задачами в области машинного обучения.",
                        "Дмитрий также затрагивает работу в машинном обучении и своем развитии в этой области.",
                    ],
                },
                {
                    "topic": "Карьера и собеседования",
                    "points": [
                        "Настя делится своим опытом прохождения собеседований.",
                        "Обсуждение трудностей в карьерном росте и ситуации на рынке труда.",
                        "Обсуждение различных карьерных путей и направлений в сфере технологий.",
                    ],
                },
                {
                    "topic": "События и встречи в индустрии",
                    "points": [
                        "Дмитрий упоминает о существующих мероприятиях, таких как 'Дата завтраки'.",
                        "Обсуждение важности участия в мероприятиях для профессионального роста.",
                        "Рассказы о других событиях, таких как ОДС-лаб.",
                    ],
                },
            ],
            "type": "json"
        },
    }
    with open("asr/results/transcription_merged.json") as f:
        transcript = json.load(f)

    summary = Summary(
        sections=sections,
        transcription=transcript,
    )

    print(summary)
    summary.save_html("summarization/results/summary.html")
    summary.save_txt("summarization/results/summary.txt")
    summary.save_json("summarization/results/summary.json")