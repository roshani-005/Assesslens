# AssessLens: Multimodal Interview Analysis

AssessLens is a local-first prototype for reviewing mock interview recordings through computer vision, speech transcription, transcript analytics, and optional LLM/VLM feedback. It demonstrates an end-to-end AI engineering workflow: data ingestion, preprocessing, inference, evaluation, application integration, privacy controls, and reproducible tests.

**Scope:** coaching and recording diagnostics only. It is not a hiring decision system and does not rank candidates.

## Features

- **Video pipeline:** validates uploaded video, samples frames with OpenCV, estimates face presence, brightness, and blur.
- **Speech pipeline:** extracts mono 16 kHz audio with FFmpeg and creates timestamped transcripts with Whisper.
- **Communication analytics:** estimates word count, words per minute, pauses, and question-specific transcript excerpts.
- **LLM/VLM integration:** optional OpenAI-compatible endpoint for rubric-guided, evidence-linked feedback; visual frames are sent only when explicitly opted in.
- **Evaluation:** WER against human-verified transcripts, face-detection precision/recall/F1 against timestamped labels, and agreement with human feedback ratings.
- **Interface and controls:** Streamlit dashboard, consent confirmation, optional temporary-file deletion, transcript download, and clear limitations.
- **Engineering:** modular Python package, unit tests, environment configuration, and an evaluation protocol.

## Architecture

```text
Video upload
  -> consent + validation
  -> OpenCV frame sampling and quality checks
  -> FFmpeg audio extraction
  -> Whisper timestamped transcription
  -> speech metrics + question windows
  -> optional LLM/VLM feedback grounded in transcript evidence
  -> Streamlit report + evaluation against human references
```

## Quick start

Requirements: Python 3.10–3.12, FFmpeg installed on PATH, and enough memory for the selected Whisper model.

```bash
git clone https://github.com/roshani-005/Assesslens.git
cd Assesslens
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Whisper downloads its selected model the first time it runs. Start with `tiny` or `base` for a lighter local setup.

## Optional LLM/VLM feedback

Set `ASSESSLENS_LLM_BASE_URL`, `ASSESSLENS_LLM_API_KEY`, and `ASSESSLENS_LLM_MODEL` in your shell environment. Do not commit API keys. The app works without an LLM; deterministic video and transcript analysis remains available. If enabled, transcript excerpts are sent to the configured provider. Sampled frames are sent only when the visual-feedback option is checked. Review the provider's privacy terms before enabling external calls.

## Evaluation

AssessLens avoids invented benchmark claims. Run:

```bash
pytest -q
```

- **WER:** compares generated transcription with a human-verified reference transcript.
- **Face detection:** precision, recall, and F1 require frame-level labels in CSV format with `timestamp_sec,face_present`.
- **Feedback quality:** compare independent human ratings for usefulness and evidence support. Agreement metrics do not establish truth or fairness.
- **Video diagnostics:** brightness, blur, and face presence are recording-quality indicators only.

See [Evaluation Protocol](docs/EVALUATION_PROTOCOL.md) for recommended methodology. Report numeric results only after evaluating on a documented, consented test set.

## Project structure

```text
app.py
assesslens/
  analytics.py
  evaluation.py
  llm_feedback.py
  media.py
  transcription.py
tests/
  test_analytics.py
  test_evaluation.py
docs/
  EVALUATION_PROTOCOL.md
.env.example
requirements.txt
pyproject.toml
```

## Responsible AI and privacy

- Get informed consent before analyzing a recording.
- Use mock interviews or explicitly consented participants.
- Keep local processing as the default and make external model calls opt-in.
- Delete temporary recordings when the session option is enabled.
- Do not infer identity, emotion, personality, health, protected traits, or employability from face/video signals.
- Do not rank applicants or automate hiring decisions.
- Treat transcripts and model output as potentially inaccurate; review all generated feedback.
- Document model versions, data conditions, known failures, and evaluation results.

## Known limitations

Haar-cascade face detection is a simple baseline and varies with lighting, camera angle, occlusion, and image quality. Whisper may misrecognize accents, names, and noisy speech. Word timestamps, speaking rate, and pauses are estimates. Question-wise segmentation currently uses user-supplied time windows. Optional VLM support depends on the configured provider's message-format compatibility.

## Resume-ready summary

Built AssessLens, a Python multimodal mock-interview analysis pipeline integrating OpenCV video diagnostics, Whisper timestamped speech transcription, question-level analytics, and optional LLM/VLM rubric feedback; implemented WER and face-detection precision/recall/F1 evaluation hooks, human-rating agreement metrics, a Streamlit interface, consent/deletion controls, and unit tests. Add measured performance figures only after running a documented evaluation.
