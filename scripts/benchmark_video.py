"""Compare Haar and optional PyTorch MTCNN video-inspection wall time.

This measures end-to-end sampled-video processing, not isolated per-frame inference.
Run on each hardware target and record the hardware/software details separately.
"""
import argparse
import statistics
import time

from assesslens.media import inspect_video, validate_video


def percentile(values, pct):
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, max(0, int(round((pct / 100) * (len(ordered) - 1)))))]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video")
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--backends", nargs="+", default=["haar", "mtcnn"], choices=["haar", "mtcnn"])
    parser.add_argument("--device", default="auto", help="auto, cpu, or cuda:0")
    args = parser.parse_args()
    if args.runs < 1:
        parser.error("--runs must be >= 1")
    valid, message = validate_video(args.video)
    if not valid:
        parser.error(message)

    for backend in args.backends:
        times = []
        for run in range(args.runs):
            start = time.perf_counter()
            result = inspect_video(args.video, face_backend=backend, device=None if args.device == "auto" else args.device)
            elapsed = time.perf_counter() - start
            if run > 0:  # Exclude first-run model initialization/warm-up from steady-state summary.
                times.append(elapsed)
        measured = times or [elapsed]
        print(f"backend={backend} device={result['face_device']} frames={result['frames_sampled']}")
        print(f"  mean_seconds={statistics.mean(measured):.4f}")
        print(f"  p50_seconds={percentile(measured, 50):.4f}")
        print(f"  p95_seconds={percentile(measured, 95):.4f}")


if __name__ == "__main__":
    main()
