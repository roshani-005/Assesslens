# AssessLens: Multimodal Interview Analysis

AssessLens is a local-first prototype for reviewing **mock interview** recordings through video diagnostics, speech transcription, transcript analytics, and optional LLM/VLM feedback. It demonstrates an end-to-end AI engineering workflow while keeping its scope limited to coaching and recording diagnostics.

**Safety scope:** AssessLens is not an identity-verification, liveness-detection, candidate-ranking, or hiring-decision system. Face presence is only a coarse framing signal.

## Implemented capabilities

- **Video diagnostics:** OpenCV frame sampling, Haar-cascade face-presence baseline, brightness, and blur estimates.
- **Speech pipeline:** FFmpeg mono 16 kHz audio extraction and timestamped Whisper transcription.
- **Communication analytics:** word count, estimated words per minute, pauses, and user-defined question time windows.
- **Optional LLM/VLM feedback:** OpenAI-compatible endpoint, rubric-guided transcript feedback, and optional opt-in frame submission.
- **Evaluation hooks:** WER against human-verified transcripts, face-detection precision/recall/F1 against timestamped labels, and human-rating agreement/MAE.
- **Privacy controls:** consent confirmation, opt-in visual sharing, and optional temporary-file deletion in the Streamlit workflow.
- **API serving:** FastAPI endpoint for video diagnostics, health check, upload-size limit, explicit consent flag, and temporary-file cleanup.
- **Container packaging:** Dockerfile for the FastAPI service and a local smoke-test workflow.
- **Engineering:** modular Python package, tests, GitHub Actions, and an evaluation protocol.

## Architecture

```text
Streamlit workflow (local)
  -> consent + video validation
  -> OpenCV Haar-cascade frame diagnostics
  -> FFmpeg audio extraction
  -> Whisper timestamped transcription
  -> speech metrics + user-defined question windows
  -> optional transcript LLM / opt-in VLM feedback
  -> report + evaluation tools

FastAPI service (container-ready)
  -> consent flag + upload validation
  -> OpenCV Haar-cascade diagnostics
  -> JSON response + temporary-file cleanup
```

## Quick start: Streamlit

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

## Run the FastAPI service

```bash
uvicorn api.main:app --reload
```

- Health check: `GET http://127.0.0.1:8000/health`
- API documentation: `http://127.0.0.1:8000/docs`
- Video diagnostics: `POST /v1/video/inspect` as multipart form data, with `file` and `consent_confirmed=true`.

The API currently serves the **OpenCV Haar-cascade baseline**. It is a service wrapper around the existing detector, not a PyTorch model-serving implementation. Authentication and production hardening are not included.

## Docker

```bash
docker build -t assesslens-api .
docker run --rm -p 8000:8000 assesslens-api
```

The Dockerfile packages the FastAPI service and FFmpeg. Docker packaging is implemented; an AWS deployment is not.

## Optional LLM/VLM feedback

Set `ASSESSLENS_LLM_BASE_URL`, `ASSESSLENS_LLM_API_KEY`, and `ASSESSLENS_LLM_MODEL` in your shell environment. Do not commit API keys. The app works without an LLM; deterministic video and transcript analysis remains available. If enabled, transcript excerpts are sent to the configured provider. Sampled frames are sent only when the visual-feedback option is checked. Review the provider's privacy terms before enabling external calls.

## Evaluation and benchmarking

Run unit tests:

```bash
pytest -q
```

Run a local end-to-end video timing experiment:

```bash
python scripts/benchmark_video.py path/to/consented_mock_interview.mp4 --runs 5
```

The script reports local whole-video timing percentiles. It does **not** establish per-frame model latency, CPU-vs-GPU speedup, concurrent serving throughput, or a production P95 claim.

- **WER:** compares generated transcription with a human-verified reference transcript.
- **Face detection:** precision, recall, and F1 require frame-level labels in CSV format with `timestamp_sec,face_present`.
- **Feedback quality:** compare independent human ratings for usefulness and evidence support. Agreement metrics do not establish truth or fairness.
- **Video diagnostics:** brightness, blur, and face presence are recording-quality indicators only.

See [Evaluation Protocol](docs/EVALUATION_PROTOCOL.md) for recommended methodology and [AWS Deployment Blueprint](docs/AWS_DEPLOYMENT.md) for a deployment plan that has not yet been executed. Report numeric results only after a documented evaluation.

## Project structure

```text
api/
  main.py
assesslens/
  analytics.py
  evaluation.py
  llm_feedback.py
  media.py
  transcription.py
docs/
  AWS_DEPLOYMENT.md
  EVALUATION_PROTOCOL.md
scripts/
  benchmark_video.py
tests/
  test_analytics.py
  test_evaluation.py
Dockerfile
.dockerignore
app.py
.env.example
requirements.txt
pyproject.toml
```

## Not yet implemented from the expanded target architecture

The following items are **not claimed as implemented**:

- PyTorch-based face detector or a validated deep-learning replacement for Haar Cascade.
- ONNX export/runtime, detector batching, or before/after optimisation results.
- Controlled CPU-vs-GPU comparison, per-frame inference benchmarks, concurrent load tests, or production P95 latency.
- Automated comparison of multiple VLM prompt variants.
- AWS ECR/ECS/S3 resources or a live cloud deployment. The AWS document is a blueprint only; the current API does not upload recordings to S3.

These require a selected detector/model artifact, labelled evaluation data, representative hardware, and cloud credentials/access. Do not add numerical improvement claims until those experiments have been run and recorded.

## Responsible AI and privacy

- Get informed consent before analyzing a recording.
- Use mock interviews or explicitly consented participants.
- Keep local processing as the default and make external model calls opt-in.
- Delete temporary recordings when the session option is enabled.
- Do not infer identity, emotion, personality, health, protected traits, or employability from face/video signals.
- Do not rank applicants or automate hiring decisions.
- Treat transcripts and model output as potentially inaccurate; review all generated feedback.
- Document model versions, data conditions, known failures, and evaluation results.

Consent and temporary-file deletion are useful safeguards, not a guarantee of legal or regulatory compliance.

## Resume-ready summary (accurate to this repository)

Built a local-first multimodal mock-interview analysis application using Python, OpenCV Haar-cascade diagnostics, Whisper transcription, optional LLM/VLM feedback, and evaluation hooks; added a FastAPI video-diagnostics service, Docker packaging, consent-aware upload handling, and reproducible local timing scripts. PyTorch/ONNX optimisation and AWS deployment remain planned extensions, not completed project results.
