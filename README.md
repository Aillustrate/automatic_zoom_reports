# Automatic zoom reports
> A tool for transcribing meeting text and summarizing it

This tool allows you to submit a recording of a meeting to receive **a structured report** on it.

**The report contains:**
- keywords,
- short summary of the meeting,
- structured summary by the topics,
- transcript, divided into speakers.

[Here](https://docs.google.com/document/d/1C43QtDXFMCdJV6ZVYyMVURxpnjXLLphLwCgW0_AMOMs/edit?usp=sharing) you can see an example of a report.

This example was created based on [the video of the career panel](https://www.youtube.com/watch?v=2lPYNu01j8I) of Data Fest Siberia 3.

## How to use

1. Clone the repository, install requirements:
```bash
git clone https://github.com/Aillustrate/automatic_zoom_reports
pip install -r requirements.txt
```

2. For the tool to work, you need to specify two API tokens in the .env:
- HuggingFace token. Make sure that you got access to [the diarization model](https://huggingface.co/pyannote/speaker-diarization-3.1)
- OpenAI API token.

4. Run via Python:
```python
# import all needed modules
from asr.transriber import Transriber
from asr.transcription import Transcription
from summarization.summarizer import Summarizer
from summarization.summary import Summary

# set your audio path and save transcription paths
audio_input_path = [AUDIO_PATH]
html_transcription_output = [PATH_TO_SAVE_HTML]
txt_transcription_output = [PATH_TO_SAVE_TXT]
json_transcription_output = [PATH_TO_SAVE_JSON]

# initialize the process
transriber = Transriber()
transcription = transriber.transcribe(audio_input_path)

# save transcript in one of the formats
transcription.to_html(html_transcription_output)
transcription.to_txt(txt_transcription_output)
transcription.to_json(json_transcription_output)

# set your token usage json and save summary paths
token_usage_report_path = [TOKEN_USAGE_STATS_PATH]
summary_html_output = [PATH_TO_SAVE_HTML]
summary_txt_output = [PATH_TO_SAVE_TXT]
summary_json_output = [PATH_TO_SAVE_JSON]

# initialize the process
summary = Summarizer(token_usage_report_path).summarize(transcription)

# save summary in one of the formats
summary.save_html(summary_html_output)
summary.save_txt(summary_txt_output)
summary.save_json(summary_json_output)
```

5. Completed build and bot for connection to zoom is coming soon =)

