from pathlib import Path
import os
import tempfile
import time

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from assesslens.media import inspect_video, validate_video

app = FastAPI(
    title="AssessLens API",
    version="0.2.0",
    description="Consent-gated mock-interview recording diagnostics. Not for hiring or identity decisions.",
)
MAX_UPLOAD_BYTES = int(os.getenv("ASSESSLENS_MAX_UPLOAD_BYTES", 100 * 1024 * 1024))
ALLOWED_SUFFIXES = {".mp4", ".mov", ".mkv", ".webm", ".avi"}


@app.get("/health")
def health():
    return {"status": "ok", "service": "assesslens-api"}


@app.post("/v1/video/inspect")
async def inspect_uploaded_video(
    file: UploadFile = File(...),
    consent_confirmed: bool = Form(...),
    face_backend: str = Form("haar"),
    device: str = Form("auto"),
):
    if not consent_confirmed:
        raise HTTPException(status_code=400, detail="Explicit recording consent is required.")
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=415, detail="Unsupported video extension.")
    payload = await file.read(MAX_UPLOAD_BYTES + 1)
    if not payload:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(payload) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Upload exceeds the configured size limit.")

    started = time.perf_counter()
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp:
            temp.write(payload)
            temp_path = Path(temp.name)
        valid, message = validate_video(temp_path)
        if not valid:
            raise HTTPException(status_code=422, detail=message)
        selected_device = None if device == "auto" else device
        result = inspect_video(temp_path, face_backend=face_backend, device=selected_device)
        result.pop("sampled_frames", None)
        return {
            "processing_seconds": round(time.perf_counter() - started, 4),
            "recording_diagnostics": result,
            "limitations": [
                "Face presence is a framing diagnostic, not identity verification or liveness detection.",
                "Detector performance varies with lighting, pose, occlusion, and image quality.",
            ],
        }
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
        await file.close()
