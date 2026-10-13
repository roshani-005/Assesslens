from pathlib import Path
import tempfile
import streamlit as st
import pandas as pd

from assesslens.media import validate_video, inspect_video, extract_audio
from assesslens.transcription import transcribe_audio
from assesslens.analytics import speaking_metrics, segment_by_questions
from assesslens.llm_feedback import generate_feedback
from assesslens.evaluation import evaluate_face_labels, word_error_rate

st.set_page_config(page_title="AssessLens", page_icon="🎙️", layout="wide")
st.title("AssessLens")
st.caption("Multimodal mock-interview review · coaching support, not a hiring decision")

with st.sidebar:
    st.header("Session controls")
    consent = st.checkbox("I have consent to analyze this recording.")
    delete_after = st.checkbox("Delete temporary files after processing", value=True)
    model_size = st.selectbox("Whisper model", ["tiny", "base", "small"], index=1)
    st.warning("Use mock interviews or recordings from people who explicitly agreed. Do not use this tool to rank candidates.")

uploaded = st.file_uploader("Upload a mock interview video", type=["mp4", "mov", "mkv", "webm"])
question_text = st.text_area("Question windows (optional)", "Tell me about yourself | 0 | 45\nDescribe a project | 45 | 120", help="One question per line: question | start_seconds | end_seconds")
enable_ai = st.checkbox("Generate optional rubric-based LLM feedback", value=False)
visual_ai = st.checkbox("Include sampled frames in the optional vision-language request", value=False, disabled=not enable_ai)
rubric = st.text_area("Answer rubric", "Relevance, structure, specificity, evidence, clarity", disabled=not enable_ai)

if uploaded and st.button("Analyze recording", type="primary"):
    if not consent:
        st.error("Please confirm consent before processing.")
        st.stop()
    if visual_ai and not enable_ai:
        st.error("Visual feedback requires optional AI feedback.")
        st.stop()
    temp_root = Path(tempfile.mkdtemp(prefix="assesslens_"))
    video_path = temp_root / uploaded.name
    video_path.write_bytes(uploaded.getvalue())
    try:
        valid, message = validate_video(video_path)
        if not valid:
            st.error(message)
            st.stop()
        with st.spinner("Checking recording quality..."):
            quality = inspect_video(video_path)
        audio_path = temp_root / "audio.wav"
        with st.spinner("Extracting audio..."):
            extract_audio(video_path, audio_path)
        with st.spinner("Transcribing speech with Whisper..."):
            transcript = transcribe_audio(audio_path, model_size=model_size)
        segments = transcript.get("segments", [])
        text = transcript.get("text", "")
        metrics = speaking_metrics(segments)
        questions = []
        for line in question_text.splitlines():
            parts = [p.strip() for p in line.split("|")]
            if len(parts) == 3:
                try:
                    questions.append({"question": parts[0], "start": float(parts[1]), "end": float(parts[2])})
                except ValueError:
                    pass
        answer_sections = segment_by_questions(segments, questions)
        a, b, c = st.columns(3)
        a.metric("Video duration", f"{quality['duration_sec']:.1f} sec")
        b.metric("Frames sampled", quality["frames_sampled"])
        c.metric("Frames with face", f"{quality['face_presence_rate']:.0%}" if quality["face_presence_rate"] is not None else "N/A")
        st.subheader("Recording quality")
        st.json({k: v for k, v in quality.items() if k not in {"sampled_frames"}})
        st.subheader("Speech analytics")
        x, y, z = st.columns(3)
        x.metric("Words", metrics["word_count"])
        y.metric("Speaking rate", f"{metrics['words_per_minute']:.1f} WPM" if metrics["words_per_minute"] is not None else "N/A")
        z.metric("Estimated pauses", metrics["pause_count"])
        st.caption("Speaking rate and pauses are approximate; transcription timestamps may be inaccurate.")
        st.subheader("Transcript")
        st.write(text or "No transcript returned.")
        if answer_sections:
            st.subheader("Question-wise excerpts")
            for item in answer_sections:
                with st.expander(f"{item['question']} ({item['start']:.0f}–{item['end']:.0f}s)"):
                    st.write(item["text"] or "No speech detected in this window.")
        if enable_ai:
            with st.spinner("Generating evidence-linked feedback..."):
                feedback = generate_feedback(text, rubric, frames=quality.get("sampled_frames") if visual_ai else None)
            st.subheader("AI feedback (review before use)")
            st.write(feedback)
        with st.expander("Evaluation tools (optional ground truth)"):
            st.write("Upload frame-level face labels CSV with timestamp_sec,face_present to calculate detection precision/recall.")
            labels_file = st.file_uploader("Face reference labels CSV", type=["csv"], key="labels")
            if labels_file:
                labels = pd.read_csv(labels_file)
                st.json(evaluate_face_labels(quality.get("frame_predictions", []), labels))
            st.write("WER compares a human-verified reference transcript with the generated transcript.")
            reference = st.text_area("Reference transcript", key="reference")
            if reference.strip():
                st.metric("Word Error Rate", f"{word_error_rate(reference, text):.3f}")
        st.download_button("Download transcript", data=text, file_name="assesslens_transcript.txt")
    except Exception as exc:
        st.error(f"Analysis failed: {exc}")
        st.info("Check that FFmpeg is installed, the video codec is supported, and the selected Whisper model fits available memory.")
    finally:
        if delete_after:
            import shutil
            shutil.rmtree(temp_root, ignore_errors=True)
            st.caption("Temporary media files were deleted. Downloaded transcript remains under your control.")

st.divider()
st.caption("AssessLens is an experimental coaching aid. Face presence measures framing/recording quality, not identity, emotion, personality, or employability.")
