def transcribe_audio(audio_path, model_size="base"):
    """Return Whisper's text and timestamped segments for an audio file."""
    try:
        import whisper
    except ImportError as exc:
        raise RuntimeError("Install openai-whisper and ensure FFmpeg is available.") from exc
    model = whisper.load_model(model_size)
    result = model.transcribe(str(audio_path), word_timestamps=True, verbose=False)
    return {"text": result.get("text", "").strip(), "segments": result.get("segments", []), "language": result.get("language")}
