import re

def _words(text):
    return re.findall(r"\b[\w']+\b", text.lower())

def speaking_metrics(segments, pause_threshold_sec=1.0):
    words = 0
    starts, ends = [], []
    previous_end = None
    pauses = []
    for segment in segments or []:
        start = float(segment.get("start", 0))
        end = float(segment.get("end", start))
        text = segment.get("text", "")
        segment_words = segment.get("words") or []
        words += len(segment_words) if segment_words else len(_words(text))
        starts.append(start)
        ends.append(end)
        if previous_end is not None and start - previous_end >= pause_threshold_sec:
            pauses.append({"start": previous_end, "end": start, "duration_sec": start - previous_end})
        previous_end = max(previous_end or end, end)
    duration = max(ends) - min(starts) if starts else 0
    wpm = words * 60 / duration if duration > 0 else None
    return {"word_count": words, "speech_duration_sec": duration, "words_per_minute": wpm, "pause_count": len(pauses), "pauses": pauses}

def segment_by_questions(segments, questions):
    output = []
    for q in questions:
        start, end = float(q["start"]), float(q["end"])
        excerpts = [s.get("text", "").strip() for s in segments if float(s.get("end", 0)) >= start and float(s.get("start", 0)) <= end]
        output.append({"question": q["question"], "start": start, "end": end, "text": " ".join(x for x in excerpts if x)})
    return output
