"""Measure end-to-end OpenCV inspection wall time on a local video.

This is a simple local benchmark, not a controlled CPU-vs-GPU or per-frame
model-inference benchmark. Run multiple times and report the hardware and video.
"""
import argparse
import statistics
import time

from assesslens.media import inspect_video, validate_video


def percentile(values, percentile):
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(round((percentile / 100) * (len(ordered) - 1)))))
    return ordered[index]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video")
    parser.add_argument("--runs", type=int, default=5)
    args = parser.parse_args()
    if args.runs < 1:
        parser.error("--runs must be at least 1")
    valid, message = validate_video(args.video)
    if not valid:
        parser.error(message)

    durations = []
    for _ in range(args.runs):
        started = time.perf_counter()
        inspect_video(args.video)
        durations.append(time.perf_counter() - started)

    print(f"runs: {len(durations)}")
    print(f"mean_end_to_end_seconds: {statistics.mean(durations):.4f}")
    print(f"p50_end_to_end_seconds: {percentile(durations, 50):.4f}")
    print(f"p95_end_to_end_seconds: {percentile(durations, 95):.4f}")
    print("Note: these are local whole-video timings, not per-frame inference latency.")


if __name__ == "__main__":
    main()
