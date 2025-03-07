import datetime
import json
import logging
from pathlib import Path
import sys
from typing import Any, Dict, List, Union

ROOT_DIR = str(Path(__file__).parent.parent)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from asr.transcription import Transcription, load_transcription_and_transcript
from summarization.summary import Summary
from summarization.scenario_manager import ScenarioManager
from summarization.llm import LLM
from summarization.parsing_utils import (parse_json_structure,
                                         process_list_structure)
from summarization.output_validation import (
    validate,
    validate_list_structure,
    validate_json_structure,
)

logging.basicConfig(level=logging.DEBUG)

class Summarizer:
    def __init__(self, token_usage_report_path, scenario_type: str = "base_meeting"):
        self.llm = LLM(token_usage_report_path)
        self.scenario_manager = ScenarioManager()
        self.scenario = self.scenario_manager.get_scenario(scenario_type)

    def process_transcript(self, transcript: List[Dict[str, Any]]):
        dialog = "\n".join([f"{r['speaker']}: {r['text']}" for r in transcript])
        speakers = list(set([r["speaker"] for r in transcript]))
        return dialog, speakers

    def summarize(
        self,
        transcription: Union[Transcription, List[Dict[str, Any]], str],
        verbose=False,
    ):
        results = {}
        transcription, _ = load_transcription_and_transcript(transcription)
        dialog = transcription.to_str(include_timestamps=False)
        for section in self.scenario.sections:
            system_prompt = self.scenario.system_context + section.prompt
            response = self.llm.get_response(system_prompt, dialog)
            if section.type == 'json':
                response = parse_json_structure(response)
                validate(response, validate_json_structure)
            elif section.type == 'list':
                response = process_list_structure(response)
                validate(response, validate_list_structure)
            results[section.id] = {
                "name": section.name,
                "content": response,
                "type": section.type
            }
            if verbose:
                logging.info(f"{section.name}: {response}")

        # TODO: убрать потом, тут для тестирования
        # with open('test_results.json', "w") as f:
        #     json.dump(results, f, indent=4, ensure_ascii=False)

        # with open('test_results.json', "r", encoding="utf-8") as f:
        #     results = json.load(f)

        #print(results)
        summary = Summary(
            sections=results,
            transcription=transcription,
        )

        return summary


if __name__ == "__main__":
    summary = Summarizer("summarization/token_usage.json").summarize(
        Transcription.from_json("asr/results/transcription_merged.json")
    )
    print(summary)
    summary.save_html("summarization/results/summary.html")
    summary.save_txt("summarization/results/summary.txt")
    summary.save_json("summarization/results/summary.json")
