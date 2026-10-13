from pathlib import Path
import subprocess
import cv2

SUPPORTED_SUFFIXES = {".mp4", ".mov", ".mkv", ".webm", ".avi"}

def validate_video(path):
    path = Path(path)
    if not path.exists() or path.stat().st_size == 0:
        return False, "The uploaded file is empty or missing."
    if path.suffix.lower() not in SUPPORTED_SUFFIXES:
        return False, "Unsupported video extension."
    cap = cv2.VideoCapture(str(path))
    opened = cap.isOpened()
    cap.release()
    if not opened:
        return False, "OpenCV could not open this video. Check the codec and file integrity."
    return True, "Video is readable."

def inspect_video(path, sample_every_sec=1.0, max_frames=120):
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError("Unable to open video.")
    fps = cap.get(cv2.CAP_PROP_FPS) or 0
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
    duration = frame_count / fps if fps > 0 else 0.0
    step = max(1, int((fps if fps > 0 else 1) * sample_every_sec))
    predictions, brightness, blur_scores, sampled = [], [], [], []
    index = 0
    while len(predictions) < max_frames:
        ok, frame = cap.read()
        if not ok:
            break
        if index % step == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness.append(float(gray.mean()))
            blur_scores.append(float(cv2.Laplacian(gray, cv2.CV_64F).var()))
            faces = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml").detectMultiScale(gray, 1.1, 4)
            predictions.append({"timestamp_sec": index / fps if fps > 0 else float(index), "face_present": int(len(faces) > 0)})
            if len(sampled) < 4:
                # Downscale and encode as JPEG bytes only for opt-in VLM analysis.
                ok_jpg, encoded = cv2.imencode(".jpg", cv2.resize(frame, (min(640, frame.shape[1]), int(frame.shape[0] * min(640, frame.shape[1]) / frame.shape[1]))))
                if ok_jpg:
                    import base64
                    sampled.append("data:image/jpeg;base64," + base64.b64encode(encoded.tobytes()).decode("ascii"))
        index += 1
    cap.release()
    count = len(predictions)
    return {
        "duration_sec": float(duration),
        "fps": float(fps),
        "frames_sampled": count,
        "face_presence_rate": sum(p["face_present"] for p in predictions) / count if count else None,
        "mean_brightness": sum(brightness) / len(brightness) if brightness else None,
        "mean_blur_score": sum(blur_scores) / len(blur_scores) if blur_scores else None,
        "frame_predictions": predictions,
        "sampled_frames": sampled,
    }

def extract_audio(video_path, output_path):
    command = ["ffmpeg", "-y", "-i", str(video_path), "-vn", "-ac", "1", "-ar", "16000", str(output_path)]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0 or not Path(output_path).exists():
        raise RuntimeError("FFmpeg audio extraction failed. Ensure FFmpeg is installed and available on PATH.")
    return Path(output_path)
