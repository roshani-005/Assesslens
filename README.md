# AssessLens: Multimodal Interview Analysis

AssessLens is a local-first prototype for reviewing **mock interview** recordings through computer vision, speech transcription, transcript analytics, and optional LLM/VLM feedback.

**Scope:** coaching and recording diagnostics only. It is not an identity-verification, liveness-detection, candidate-ranking, or hiring-decision system. Face presence is a coarse framing signal.

## Implemented features

- **Computer vision:** OpenCV video sampling, Haar-cascade baseline, and an optional PyTorch-backed MTCNN face detector (facenet-pytorch). Select the backend and CPU/CUDA device in the Streamlit sidebar.
- **Recording quality:** estimates face presence, brightness, and blur.
- **Speech pipeline:** FFmpeg extracts mono 16 kHz audio; Whisper creates timestamped transcripts.
- **Communication analytics:** word count, estimated speaking rate, pauses, and user-defined question time windows.
- **LLM/VLM:** optional OpenAI-compatible rubric-guided feedback; sampled frames are sent only when visual feedback is explicitly enabled.
- **Evaluation:** WER against human-verified transcripts, face-detection precision/recall/F1 against timestamped labels, and human-rating agreement/MAE.
- **Serving:** FastAPI health endpoint and consent-gated video-inspection endpoint.
- **Container:** Dockerfile for the FastAPI service.
- **Privacy controls:** consent confirmation, optional temporary-file deletion in the Streamlit flow, and opt-in external visual analysis.

## Face detector backends

Haar Cascade is the lightweight default and is included with OpenCV. The optional MTCNN backend uses a pretrained PyTorch model through facenet-pytorch.

Install the optional deep-learning dependencies:

~~~bash
pip install -r requirements-cv.txt
~~~

In the Streamlit sidebar choose:
- **haar**: lightweight OpenCV baseline.
- **mtcnn**: PyTorch-backed face detector; model weights are downloaded by the package on first use.
- Device: **auto**, **cpu**, or **cuda:0**. CUDA requires a compatible PyTorch build and NVIDIA GPU.

You can also select the backend through the ASSESSLENS_FACE_BACKEND and ASSESSLENS_DEVICE environment variables.

MTCNN is a different detector architecture, not a guarantee of better accuracy. Evaluate both on the same consented, human-labelled dataset before choosing one for a use case.

## Quick start: Streamlit

Requirements: Python 3.10–3.12, FFmpeg on PATH, and enough memory for the selected Whisper model.

~~~bash
git clone https://github.com/roshani-005/Assesslens.git
cd Assesslens
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
# Optional PyTorch detector:
pip install -r requirements-cv.txt
streamlit run app.py
~~~

## FastAPI model-serving endpoint

Start the API:

~~~bash
uvicorn api.main:app --reload
~~~

- Health: http://127.0.0.1:8000/health
- Interactive API docs: http://127.0.0.1:8000/docs
- Video diagnostics: POST /v1/video/inspect using multipart fields file, consent_confirmed=true, optional face_backend=haar|mtcnn, and device=auto|cpu|cuda:0.

The endpoint enforces a configurable upload limit (ASSESSLENS_MAX_UPLOAD_BYTES, default 100 MiB) and deletes its temporary upload after processing. It does not include authentication or production-grade network protections.

## Docker

Build and run the API service:

~~~bash
docker build -t assesslens-api .
docker run --rm -p 8000:8000 assesslens-api
~~~

The Docker image installs the base requirements and serves the Haar backend. To run MTCNN in a container, install the optional PyTorch dependencies and choose a compatible CPU/CUDA base image; GPU passthrough also requires NVIDIA Container Toolkit.

## Benchmarking

Compare Haar and MTCNN on the same local video:

~~~bash
pip install -r requirements-cv.txt
python scripts/benchmark_video.py path/to/consented_mock_interview.mp4 --runs 6 --backends haar mtcnn --device auto
~~~

The script excludes the first run (model initialization/warm-up) from its steady-state summary and reports whole-video mean, P50, and P95 processing times. This is not isolated per-frame inference latency or a concurrent API load test. Record CPU/GPU model, RAM/VRAM, OS, Python, PyTorch, OpenCV, video dimensions, sampling interval, and frame count with any reported results.

## Evaluation

Run tests:

~~~bash
pytest -q
~~~

- **Face detector:** use frame-level reference labels in CSV format with timestamp_sec,face_present; report precision, recall, and F1 for each backend.
- **Speech transcription:** WER compares the generated transcript with a human-verified reference.
- **Feedback:** compare independent human ratings for usefulness and evidence support. Agreement does not prove truth or fairness.
- **Recording diagnostics:** brightness, blur, and face presence are proxies, not quality guarantees.

See docs/EVALUATION_PROTOCOL.md. Do not claim accuracy or latency improvements until the same test set and hardware have been used for a documented comparison.

## Current limitations and not-yet-implemented items

- **ONNX export/runtime and ONNX-specific optimisation are not implemented.** MTCNN is currently run through PyTorch.
- Detector batching and a measured before/after optimisation result are not implemented.
- No controlled CPU-vs-GPU comparison or concurrent API load test is included; the benchmark script helps collect local whole-video timings.
- Automated VLM prompt-variant experiments are not implemented.
- AWS ECR/ECS/S3 resources and a live deployment are not configured. No recordings are uploaded to S3.

These are future extensions, not current project results. Never invent performance figures.

## Responsible AI and privacy

- Get informed consent before analyzing a recording; use mock interviews or explicitly consented participants.
- Keep local processing as the default and make external model calls opt-in.
- Delete temporary recordings when the session option is enabled.
- Do not infer identity, emotion, personality, health, protected traits, or employability from face/video signals.
- Do not rank applicants or automate hiring decisions.
- Treat transcripts and generated feedback as potentially inaccurate; review all output.
- Consent and temporary-file deletion are safeguards, not a guarantee of legal or regulatory compliance.

## Resume-ready summary (accurate to current code)

Built a multimodal mock-interview analysis application using Python, OpenCV Haar Cascade and optional PyTorch MTCNN face detection, Whisper transcription, optional LLM/VLM feedback, and evaluation hooks; added a FastAPI video-diagnostics service, Docker packaging, selectable CPU/CUDA inference, and a local detector benchmarking script. ONNX optimisation and AWS deployment are not yet implemented.
