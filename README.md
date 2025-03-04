# Automatic zoom reports
> A tool for transcribing meeting text and summarizing it

This tool allows you to submit a recording of a meeting and receive **a structured report** on it.

**A report contains:**
- keywords,
- short summary of the meeting,
- structured summary by the topics,
- transcript, divided by speakers.

[Here](https://docs.google.com/document/d/1C43QtDXFMCdJV6ZVYyMVURxpnjXLLphLwCgW0_AMOMs/edit?usp=sharing) you can see an example of a report.

This example was created based on [the video of the career panel](https://www.youtube.com/watch?v=2lPYNu01j8I) of Data Fest Siberia 3.

## How to use

1. Clone the repository, install requirements:
```bash
git clone https://github.com/Aillustrate/automatic_zoom_reports
bash install.sh
```

2. For the tool to work, you need to specify two API tokens in the `.env`:
- `HF_TOKEN`. Make sure that you got access to [the diarization model](https://huggingface.co/pyannote/speaker-diarization-3.1)
- `OPENAI_API_KEY`.

4. Run via Python:
```python
# import all needed modules
from automatic_zoom_reports.asr.transriber import Transcriber
from automatic_zoom_reports.asr.transcription import Transcription
from automatic_zoom_reports.summarization.summarizer import Summarizer
from automatic_zoom_reports.summarization.summary import Summary

# set your audio path
audio_input_path = "your_audio.mp3"

# initialize the process
transcriber = Transcriber()
transcription = transcriber.transcribe(audio_input_path)

# save transcript in one of the formats
transcription.save_html()
transcription.save_txt()
transcription.save_json()

# set token_usage_report_path to keep track of gpt token usage
token_usage_report_path = "token_usage.json"

# initialize the process
summary = Summarizer(token_usage_report_path).summarize(transcription)

# save summary in one of the formats
summary.save_html()
summary.save_txt()
summary.save_json()
```

5. Completed build and bot for connection to zoom is coming soon =)

