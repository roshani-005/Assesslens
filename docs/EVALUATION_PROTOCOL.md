# Evaluation protocol

## Purpose
AssessLens supports mock-interview practice and recording-quality review. It is not a candidate selection, ranking, personality, emotion, or employability assessment system.

## Evaluation data
Use only recordings with informed consent. Prefer staged mock interviews. Store reference labels separately from media, limit access, and delete raw media after evaluation.

## Metrics
- Face detection: frame-level precision, recall, and F1 against human labels. Match predictions and reference timestamps within 0.5 seconds by default.
- Speech transcription: word error rate (WER) against a human-verified reference transcript.
- Answer feedback: independent human ratings for usefulness and evidence support; report exact agreement and mean absolute error when ratings share a scale.
- Recording quality: report sampling rate, number of frames, brightness and blur summaries. These are proxies, not quality guarantees.

## Reporting
Record dataset size, recording conditions, language, hardware, model/version, model settings, exclusion criteria, and limitations. Include confidence intervals when the sample supports them. Do not claim a performance number without a documented evaluation run.

## Bias and safety checks
Review face detection across lighting, camera position, skin tone, glasses, head coverings, and occlusion where participants voluntarily provide relevant test conditions. Do not infer protected traits from video. Do not use face presence as an answer-quality or hiring signal. Review transcription errors across accents, languages, noise levels, and speaking styles. Keep AI feedback evidence-linked and subject to human review.
