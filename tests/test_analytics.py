from assesslens.analytics import speaking_metrics, segment_by_questions

def test_speaking_metrics_counts_words_and_pauses():
    segments = [{"start": 0, "end": 2, "text": "Hello there"},
                {"start": 4, "end": 6, "text": "How are you"}]
    result = speaking_metrics(segments)
    assert result["word_count"] == 5
    assert result["pause_count"] == 1
    assert round(result["words_per_minute"], 2) == 50.0

def test_question_windows():
    segments = [{"start": 1, "end": 3, "text": "First answer"},
                {"start": 8, "end": 10, "text": "Second answer"}]
    result = segment_by_questions(segments, [{"question": "Q1", "start": 0, "end": 5}])
    assert result[0]["text"] == "First answer"
