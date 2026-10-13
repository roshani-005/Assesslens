import re
import numpy as np

def _tokens(text):
    return re.findall(r"\w+", str(text).lower())

def word_error_rate(reference, hypothesis):
    """Compute WER with word-level Levenshtein distance."""
    ref, hyp = _tokens(reference), _tokens(hypothesis)
    if not ref:
        return 0.0 if not hyp else 1.0
    previous = list(range(len(hyp) + 1))
    for i, token in enumerate(ref, 1):
        current = [i]
        for j, candidate in enumerate(hyp, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (token != candidate)))
        previous = current
    return previous[-1] / len(ref)

def evaluate_face_labels(predictions, reference_df, tolerance_sec=0.5):
    required = {"timestamp_sec", "face_present"}
    if not required.issubset(reference_df.columns):
        raise ValueError("Reference CSV must contain timestamp_sec,face_present.")
    if not predictions:
        raise ValueError("No frame predictions available.")
    truth, predicted = [], []
    for row in reference_df.to_dict("records"):
        timestamp = float(row["timestamp_sec"])
        nearest = min(predictions, key=lambda p: abs(float(p["timestamp_sec"]) - timestamp))
        if abs(float(nearest["timestamp_sec"]) - timestamp) <= tolerance_sec:
            truth.append(int(row["face_present"]))
            predicted.append(int(nearest["face_present"]))
    if not truth:
        raise ValueError("No reference labels matched sampled frames within tolerance.")
    tp = sum(y == 1 and p == 1 for y, p in zip(truth, predicted))
    fp = sum(y == 0 and p == 1 for y, p in zip(truth, predicted))
    fn = sum(y == 1 and p == 0 for y, p in zip(truth, predicted))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {"matched_frames": len(truth), "precision": precision, "recall": recall, "f1": 2*precision*recall/(precision+recall) if precision+recall else 0.0}

def agreement_with_human_ratings(model_ratings, human_ratings):
    if len(model_ratings) != len(human_ratings) or not model_ratings:
        raise ValueError("Rating lists must be non-empty and have equal lengths.")
    return {"exact_agreement": float(np.mean(np.array(model_ratings) == np.array(human_ratings))),
            "mean_absolute_error": float(np.mean(np.abs(np.array(model_ratings) - np.array(human_ratings))))}
