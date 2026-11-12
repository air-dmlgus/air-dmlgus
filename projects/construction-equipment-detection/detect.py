"""Video object detection demo with a user-provided YOLOv5 model.

Requires a local, trusted YOLOv5 checkout and compatible weights.
This is illustrative portfolio code, not the original capstone source.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import torch


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YOLOv5 AVM video inference demo")
    parser.add_argument("--weights", type=Path, required=True, help="YOLOv5-compatible .pt file")
    parser.add_argument("--source", default="0", help="video path or camera index (0)")
    parser.add_argument("--yolov5-repo", type=Path, required=True, help="trusted local YOLOv5 repo")
    parser.add_argument("--output", type=Path, default=Path("result.mp4"))
    parser.add_argument("--confidence", type=float, default=0.35)
    parser.add_argument("--person-only", action="store_true", help="show only person detections")
    parser.add_argument("--max-frames", type=int, default=0, help="0 means no limit")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.weights.is_file():
        raise FileNotFoundError(f"Model weights not found: {args.weights}")
    if not (args.yolov5_repo / "hubconf.py").is_file():
        raise FileNotFoundError(f"Not a YOLOv5 checkout: {args.yolov5_repo}")
    if not 0 <= args.confidence <= 1:
        raise ValueError("confidence must be between 0 and 1")
    if args.max_frames < 0:
        raise ValueError("max-frames must be >= 0")

    model = torch.hub.load(
        str(args.yolov5_repo.resolve()),
        "custom",
        path=str(args.weights.resolve()),
        source="local",
    )
    model.conf = args.confidence
    source = int(args.source) if args.source.isdigit() else args.source
    capture = cv2.VideoCapture(source)
    if not capture.isOpened():
        raise RuntimeError(f"Unable to open video source: {args.source}")

    fps = capture.get(cv2.CAP_PROP_FPS)
    if fps <= 0 or fps > 240:
        fps = 20.0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    writer = None
    log_path = args.output.with_suffix(".jsonl")
    frame_id = 0
    try:
        with log_path.open("w", encoding="utf-8") as log:
            while True:
                ok, frame = capture.read()
                if not ok:
                    break
                if writer is None:
                    height, width = frame.shape[:2]
                    writer = cv2.VideoWriter(
                        str(args.output),
                        cv2.VideoWriter_fourcc(*"mp4v"),
                        fps,
                        (width, height),
                    )
                    if not writer.isOpened():
                        raise RuntimeError("Unable to create output video")

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                predictions = model(rgb)
                detections = []
                for xmin, ymin, xmax, ymax, confidence, cls in predictions.xyxy[0].cpu().tolist():
                    label = model.names[int(cls)]
                    if args.person_only and label != "person":
                        continue
                    x1, y1, x2, y2 = map(int, (xmin, ymin, xmax, ymax))
                    detections.append({
                        "label": label,
                        "confidence": round(float(confidence), 4),
                        "bbox": [x1, y1, x2, y2],
                    })
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 255), 2)
                    cv2.putText(
                        frame, f"{label} {confidence:.2f}", (x1, max(20, y1 - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2,
                    )
                log.write(json.dumps({"frame": frame_id, "detections": detections}) + "\n")
                writer.write(frame)
                frame_id += 1
                if args.max_frames and frame_id >= args.max_frames:
                    break
    finally:
        capture.release()
        if writer is not None:
            writer.release()
    print(f"Processed {frame_id} frames. Video: {args.output}, log: {log_path}")


if __name__ == "__main__":
    main()
