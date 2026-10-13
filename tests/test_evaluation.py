import pandas as pd
from assesslens.evaluation import word_error_rate, evaluate_face_labels, agreement_with_human_ratings

def test_wer():
    assert word_error_rate("the cat sat", "the cat sat") == 0
    assert round(word_error_rate("the cat sat", "the cat"), 3) == 0.333

def test_face_metrics():
    preds = [{"timestamp_sec": 0.0, "face_present": 1}, {"timestamp_sec": 1.0, "face_present": 0}]
    refs = pd.DataFrame([{"timestamp_sec": 0.1, "face_present": 1}, {"timestamp_sec": 1.1, "face_present": 1}])
    metrics = evaluate_face_labels(preds, refs)
    assert metrics["matched_frames"] == 2
    assert metrics["precision"] == 1
    assert metrics["recall"] == 0.5

def test_human_rating_agreement():
    result = agreement_with_human_ratings([3, 4, 5], [3, 3, 5])
    assert round(result["exact_agreement"], 2) == 0.67
    assert round(result["mean_absolute_error"], 2) == 0.33
