# AssessLens: Multimodal Interview Analysis

AssessLens is a local-first prototype for reviewing mock interview recordings with video quality checks, speech transcription, speaking-pattern summaries, and evidence-linked answer feedback. It combines deterministic computer-vision/audio signals with optional LLM/VLM analysis. It is a coaching aid, not a hiring decision system.

## What it does

- Checks video readability and face presence with OpenCV.
- Extracts audio from video and transcribes it with Whisper.
- Calculates speaking rate and pause estimates from timestamped segments.
- Organizes transcript excerpts by question using configurable question windows.
- Offers rubric-guided feedback through an optional OpenAI-compatible LLM/VLM endpoint.
- Reports face-detection precision/recall when reference labels are supplied, and transcript WER when a reference transcript is supplied.
- Shows results in Streamlit with explicit consent, local processing defaults, and deletion controls.

## Architecture

```text
Video upload
  ├─ consent + file validation
  ├─ OpenCV: sampled frames, face presence, recording quality
  ├─ FFmpeg: audio extraction
  ├─ Whisper: timestamped transcription
  ├─ analytics: speaking rate, pause estimates, question windows
  ├─ optional LLM/VLM: rubric-based feedback grounded in transcript evidence
  └─ Streamlit report: metrics, excerpts, limitations, delete session data
```

## Quick start

Python 3.10–3.11 is recommended. FFmpeg must be installed and available on PATH for audio extraction.

```bash
git clone https://github.com/roshani-005/Assesslens.git
cd Assesslens
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Whisper downloads its model on first use. Choose a smaller model such as `base` for faster local runs. Processing time depends on video duration and hardware.

## Optional LLM feedback

Set an OpenAI-compatible endpoint and key in your environment. The app runs without an LLM; deterministic checks and transcript analytics remain available.

```bash
# PowerShell
$env:ASSESSLENS_LLM_BASE_URL="https://api.openai.com/v1"
$env:ASSESSLENS_LLM_API_KEY="your-key"
$env:ASSESSLENS_LLM_MODEL="your-model"

# macOS/Linux
export ASSESSLENS_LLM_BASE_URL="https://api.openai.com/v1"
export ASSESSLENS_LLM_API_KEY="your-key"
export ASSESSLENS_LLM_MODEL="your-model"
```

Do not commit API keys or real interview recordings. The optional provider receives transcript excerpts and, if visual feedback is enabled, sampled frames. Review provider privacy terms before enabling it.

## Evaluation

AssessLens does not invent performance scores when ground truth is missing.

- **Face detection:** precision/recall/F1 require frame-level reference labels in CSV format with `timestamp_sec,face_present` (face_present is 0 or 1). Predicted labels use the configured detection threshold.
- **Transcription:** word error rate (WER) requires a human-verified reference transcript.
- **Answer feedback:** human reviewers rate feedback usefulness and evidence support; model-generated comments are not ground truth.
- **Speaking rate:** estimated from Whisper word timestamps when available; pauses are approximate and depend on transcript segmentation.

## Project layout

```text
app.py
assesslens/
  analytics.py       # transcript metrics and question windows
  evaluation.py      # WER, face precision/recall, human agreement
  llm_feedback.py   # optional rubric-based feedback
  media.py           # validation, frame checks, audio extraction
  transcription.py  # Whisper wrapper
tests/
  test_analytics.py
  test_evaluation.py
```

## Privacy and responsible use

- Obtain informed consent before recording or analyzing anyone.
- Use mock interviews or recordings from participants who explicitly agreed.
- Provide deletion controls and avoid retaining recordings by default.
- Face presence is a recording-quality signal, not an identity, emotion, personality, or employability signal.
- Do not rank candidates or make automated hiring decisions from these outputs.
- Inspect all AI-generated feedback; it may be wrong or unsupported.
- Local processing is the default. Optional external model calls are opt-in.

## Limitations

Whisper transcripts and timestamps contain errors; pause and speaking-rate estimates are approximate. Face detection varies with lighting, camera angle, skin tone, occlusion, and model choice. The current baseline detects faces with OpenCV's Haar cascade and is intended for a reproducible prototype, not production-grade biometrics. Question segmentation is based on user-provided timestamps rather than automatic interviewer-turn detection.

## Tests

```bash
pytest -q
```

## Resume-ready project summary

Built AssessLens, a multimodal mock-interview analysis pipeline using Python, OpenCV, Whisper, Streamlit, and optional LLM/VLM APIs; added video-quality checks, timestamped transcription, speaking-pattern analytics, evidence-linked rubric feedback, and evaluation hooks for face-detection precision/recall, transcription WER, and human-rating agreement.

Only claim measured performance figures after running evaluation on a documented, consented test set.
