import numpy as np
import pytest

from assesslens.face_detection import HaarFaceDetector, get_face_detector


def test_haar_detector_returns_no_faces_for_blank_frame():
    detector = HaarFaceDetector()
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    assert len(detector.detect(frame)) == 0


def test_unknown_detector_backend_is_rejected():
    with pytest.raises(ValueError, match="Unknown face backend"):
        get_face_detector("not-a-detector")
