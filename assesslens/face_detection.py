"""Face detector backends used by AssessLens.

Haar is the lightweight default. MTCNN is an optional PyTorch-backed face detector
provided by facenet-pytorch. MTCNN weights are downloaded by the library on first use.
"""
from functools import lru_cache
import os

import cv2


class HaarFaceDetector:
    name = "opencv-haar-cascade"

    def __init__(self):
        self._cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        if self._cascade.empty():
            raise RuntimeError("OpenCV could not load the Haar-cascade face detector.")

    def detect(self, frame_bgr):
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        return self._cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)


class MTCNNFaceDetector:
    name = "pytorch-mtcnn"

    def __init__(self, device=None, min_face_size=20, thresholds=(0.6, 0.7, 0.7)):
        try:
            import torch
            from facenet_pytorch import MTCNN
        except ImportError as exc:
            raise RuntimeError("The PyTorch MTCNN backend requires optional dependencies. Install them with: pip install -r requirements-cv.txt") from exc
        selected_device = device or ("cuda:0" if torch.cuda.is_available() else "cpu")
        self.device = selected_device
        self._model = MTCNN(
            image_size=160, margin=0, min_face_size=min_face_size,
            thresholds=list(thresholds), factor=0.709, post_process=False,
            keep_all=True, device=selected_device,
        )

    def detect(self, frame_bgr):
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        boxes, _ = self._model.detect(frame_rgb)
        return [] if boxes is None else boxes


@lru_cache(maxsize=2)
def _cached_detector(backend, device):
    if backend == "haar":
        return HaarFaceDetector()
    if backend == "mtcnn":
        return MTCNNFaceDetector(device=device)
    raise ValueError("Unknown face backend. Choose 'haar' or 'mtcnn'.")


def get_face_detector(backend=None, device=None):
    backend = (backend or os.getenv("ASSESSLENS_FACE_BACKEND", "haar")).lower()
    device = device or os.getenv("ASSESSLENS_DEVICE") or None
    return _cached_detector(backend, device)
