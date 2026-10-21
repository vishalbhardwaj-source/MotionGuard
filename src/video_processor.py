import colorsys
import json
from pathlib import Path

import cv2
from ultralytics import YOLO


def inspect_video(video_path):
    path = Path(video_path)

    if not path.is_file():
        raise FileNotFoundError(f"Video not found: {path}")

    cap = cv2.VideoCapture(str(path))

    if not cap.isOpened():
        raise ValueError(f"Could not open video: {path}")

    try:
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        return {
            "path": str(path),
            "fps": fps,
            "frame_count": frame_count,
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "duration_seconds": (
                frame_count / fps if fps > 0 else None
            ),
        }
    finally:
        cap.release()


def save_frame(video_path, timestamp_seconds, output_path):
    if timestamp_seconds < 0:
        raise ValueError("Timestamp cannot be negative.")

    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        raise ValueError("Could not open video.")

    try:
        cap.set(cv2.CAP_PROP_POS_MSEC, timestamp_seconds * 1000)
        success, frame = cap.read()

        if not success:
            raise ValueError(
                "Could not read a frame at that timestamp."
            )

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        if not cv2.imwrite(str(output), frame):
            raise OSError("Could not save the frame.")

        return str(output)
    finally:
        cap.release()


def extract_and_annotate_event_evidence(
    video_path,
    event,
    trajectory_records=None,
    output_path=None,
):
    """
    Extract the exact video frame at the event timestamp and draw visual annotations.
    Places a clean semi-transparent HUD at the bottom to avoid obscuring vehicles.
    """
    path = Path(video_path)
    if not path.is_file():
        raise FileNotFoundError(f"Video file not found: {path}")

    timestamp = event.get("evidence_timestamp_seconds")
    if timestamp is None:
        timestamp = event.get("minimum_distance_timestamp_seconds", event.get("start_seconds", 0.0))

    try:
        ts = max(0.0, float(timestamp))
    except (ValueError, TypeError):
        ts = 0.0

    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {path}")

    try:
        cap.set(cv2.CAP_PROP_POS_MSEC, ts * 1000)
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_MSEC, 0)
            ret, frame = cap.read()
            if not ret:
                raise ValueError("Could not read frame from video.")

        height, width = frame.shape[:2]
        track_ids = set(event.get("track_ids", []))

        # Highlight bounding boxes for involved tracks at this timestamp
        if trajectory_records and track_ids:
            for tid in sorted(track_ids):
                matching = [
                    r for r in trajectory_records
                    if r.get("track_id") == tid
                    and abs(float(r.get("timestamp_seconds", -999)) - ts) <= 0.45
                ]
                if not matching:
                    continue
                best_r = min(matching, key=lambda r: abs(float(r.get("timestamp_seconds", 0)) - ts))
                bbox = best_r.get("bbox_xyxy")
                if bbox and len(bbox) == 4:
                    x1, y1, x2, y2 = [int(round(v)) for v in bbox]
                    x1 = max(0, min(width - 1, x1))
                    x2 = max(0, min(width - 1, x2))
                    y1 = max(0, min(height - 1, y1))
                    y2 = max(0, min(height - 1, y2))
                    cls_name = best_r.get("class_name", "vehicle")

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 230), 2)
                    label = f"TRACK {tid} ({cls_name})"
                    label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.48, 1)
                    lbl_w = label_size[0] + 8
                    lbl_h = label_size[1] + 8
                    lbl_y1 = max(0, y1 - lbl_h)
                    lbl_y2 = y1 if lbl_y1 < y1 else y1 + lbl_h
                    cv2.rectangle(frame, (x1, lbl_y1), (x1 + lbl_w, lbl_y2), (0, 0, 230), -1)
                    cv2.putText(
                        frame,
                        label,
                        (x1 + 4, lbl_y2 - 4),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.48,
                        (255, 255, 255),
                        1,
                        cv2.LINE_AA,
                    )

        # Draw clean, non-intrusive bottom HUD overlay (semi-transparent)
        hud_height = min(75, int(height * 0.12))
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, height - hud_height), (width, height), (15, 23, 42), -1)
        cv2.addWeighted(overlay, 0.78, frame, 0.22, 0, frame)

        event_id = event.get("event_id", "EVENT")
        min_dist = event.get("minimum_distance_px", "N/A")
        closing = event.get("peak_closing_speed_px_per_second", "N/A")

        dist_str = f"{min_dist:.1f} px" if isinstance(min_dist, (int, float)) else str(min_dist)
        closing_str = f"{closing:.1f} px/s" if isinstance(closing, (int, float)) else str(closing)

        title_text = f"{event_id} | CLOSEST APPROACH: {ts:.2f}s | Min Separation: {dist_str}"
        detail_text = f"Peak Closing Speed: {closing_str} | Involved Tracks: {list(track_ids)}"

        cv2.putText(
            frame,
            title_text,
            (18, height - int(hud_height * 0.55)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.62,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            frame,
            detail_text,
            (18, height - int(hud_height * 0.20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            (203, 213, 225),
            1,
            cv2.LINE_AA,
        )

        if output_path is None:
            output_dir = Path("outputs/evidence")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{event_id}_evidence.jpg"

        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(out_file), frame)
        return str(out_file)
    finally:
        cap.release()




def track_video(
    video_path,
    output_path,
    progress_callback=None,
    confidence=0.25,
    model=None,
    trajectory_output_path=None,
    imgsz=640,
    frame_skip=0,
):
    """Track objects in a video and save an annotated MP4.

    Args:
        imgsz:      YOLO inference image size. Smaller = faster (e.g. 320 or 416).
        frame_skip: Process every (frame_skip+1)th frame. 0 = all, 1 = every other.
    """
    import torch

    input_path = Path(video_path)
    output_file = Path(output_path)

    if not input_path.is_file():
        raise FileNotFoundError(f"Video not found: {input_path}")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    info = inspect_video(input_path)
    total_frames = info["frame_count"]
    fps = info["fps"] if info["fps"] > 0 else 30.0

    if total_frames <= 0:
        raise ValueError("The video contains no readable frames.")

    if model is None:
        model = YOLO("yolo11n.pt")

    # Use GPU when available; FP16 roughly halves inference time
    device = "cuda" if torch.cuda.is_available() else "cpu"
    use_half = device == "cuda"

    cap = cv2.VideoCapture(str(input_path))

    if not cap.isOpened():
        raise RuntimeError("Could not open input video.")

    writer = None
    trajectory_file = None
    frames_processed = 0
    frames_with_tracks = 0
    track_ids_seen = set()
    annotated_frame = None

    if trajectory_output_path is not None:
        trajectory_path = Path(trajectory_output_path)
        trajectory_path.parent.mkdir(parents=True, exist_ok=True)
        trajectory_file = trajectory_path.open(
            "w", encoding="utf-8"
        )

    try:
        writer = cv2.VideoWriter(
            str(output_file),
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (info["width"], info["height"]),
        )

        if not writer.isOpened():
            raise RuntimeError("Could not create output video.")
        trajectory_history = {}
        last_seen_frame = {}
        raw_frame_index = 0
        while True:
            success, frame = cap.read()
            if not success:
                break

            # Frame-skipping: re-use last annotated frame for skipped frames
            if frame_skip > 0 and raw_frame_index % (frame_skip + 1) != 0:
                raw_frame_index += 1
                frames_processed += 1
                if annotated_frame is not None:
                    writer.write(annotated_frame)
                continue

            raw_frame_index += 1

            result = model.track(
                source=frame,
                persist=True,
                tracker="bytetrack.yaml",
                device=device,
                half=use_half,
                imgsz=imgsz,
                conf=confidence,
                verbose=False,
            )[0]

            annotated_frame = result.plot()


            if result.boxes is not None and result.boxes.id is not None:
                boxes = result.boxes
                ids = boxes.id.int().cpu().tolist()
                track_ids_seen.update(ids)

                if ids:
                    frames_with_tracks += 1

                xyxy = boxes.xyxy.cpu().tolist()
                classes = boxes.cls.int().cpu().tolist()

                for track_id, bbox, class_id in zip(
                    ids, xyxy, classes
                ):
                    center = (
                        int((bbox[0] + bbox[2]) / 2),
                        int((bbox[1] + bbox[3]) / 2),
                    )

                    # Draw a colored bounding box and track ID label.
                    hue = (track_id * 0.61803398875) % 1.0
                    rgb = colorsys.hsv_to_rgb(hue, 0.85, 1.0)
                    color = tuple(
                        int(channel * 255)
                        for channel in reversed(rgb)
                    )

                    x1, y1, x2, y2 = [
                        int(value) for value in bbox
                    ]

                    cv2.rectangle(
                        annotated_frame,
                        (x1, y1),
                        (x2, y2),
                        color,
                        2,
                        cv2.LINE_AA,
                    )

                    label = (
                        f"ID {track_id} | "
                        f"{model.names[int(class_id)]}"
                    )

                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 0.5
                    thickness = 1

                    (text_width, text_height), baseline = (
                        cv2.getTextSize(
                            label, font, font_scale, thickness
                        )
                    )

                    label_y = max(y1, text_height + 8)

                    cv2.rectangle(
                        annotated_frame,
                        (x1, label_y - text_height - 8),
                        (x1 + text_width + 8, label_y + baseline - 4),
                        color,
                        -1,
                    )

                    cv2.putText(
                        annotated_frame,
                        label,
                        (x1 + 4, label_y - 4),
                        font,
                        font_scale,
                        (255, 255, 255),
                        thickness,
                        cv2.LINE_AA,
                    )

                    points = trajectory_history.setdefault(
                        track_id, []
                    )
                    points.append(center)


                    if len(points) > 30:
                        del points[:-30]

                    last_seen_frame[track_id] = frames_processed


                    if trajectory_file is not None:
                        record = {
                            "frame_index": frames_processed,
                            "timestamp_seconds": round(
                                frames_processed / fps, 3
                            ),
                            "track_id": track_id,
                            "class_name": model.names[int(class_id)],
                            "bbox_xyxy": [
                                round(float(value), 2)
                                for value in bbox
                            ],
                            "center_xy": [
                                round(float((bbox[0] + bbox[2]) / 2), 2),
                                round(float((bbox[1] + bbox[3]) / 2), 2),
                            ],
                        }
                        trajectory_file.write(
                            json.dumps(record) + "\n"
                        )
            # Remove trails for objects not seen in the last 10 frames.
            stale_ids = [
                track_id
                for track_id in trajectory_history
                if frames_processed - last_seen_frame.get(
                    track_id, frames_processed
                ) > 10
            ]

            for track_id in stale_ids:
                del trajectory_history[track_id]
                last_seen_frame.pop(track_id, None)



            # Draw dotted trajectory trails for each tracked object.
            for track_id, points in trajectory_history.items():
                if not points:
                    continue

                hue = (track_id * 0.61803398875) % 1.0
                rgb = colorsys.hsv_to_rgb(hue, 0.85, 1.0)
                color = tuple(
                    int(channel * 255) for channel in reversed(rgb)
                )

                # Draw evenly spaced dots along the trajectory.
                for index, point in enumerate(points):
                    if index % 3 == 0:
                        cv2.circle(
                            annotated_frame,
                            point,
                            3,
                            color,
                            -1,
                            cv2.LINE_AA,
                        )

                # Highlight the current position.
                current = points[-1]
                cv2.circle(
                    annotated_frame,
                    current,
                    7,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )
                cv2.circle(
                    annotated_frame,
                    current,
                    4,
                    color,
                    -1,
                    cv2.LINE_AA,
                )

                # Mark the latest tracked position.
                current = points[-1]
                cv2.circle(
                    annotated_frame,
                    current,
                    7,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )
                cv2.circle(
                    annotated_frame,
                    current,
                    4,
                    color,
                    -1,
                    cv2.LINE_AA,
                )

                # Highlight the object's latest position.
                current = points[-1]

                cv2.circle(
                    annotated_frame,
                    current,
                    7,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )
                cv2.circle(
                    annotated_frame,
                    current,
                    4,
                    color,
                    -1,
                    cv2.LINE_AA,
                )

            writer.write(annotated_frame)
           


            frames_processed += 1

            if progress_callback and (
                frames_processed % 5 == 0
                or frames_processed == total_frames
            ):
                progress_callback(
                    min(frames_processed / total_frames, 1.0)
                )


    finally:
        cap.release()
        if writer is not None:
            writer.release()
        if trajectory_file is not None:
            trajectory_file.close()

    return {
        "output_path": str(output_file),
        "frames_processed": frames_processed,
        "frames_with_tracks": frames_with_tracks,
        "distinct_track_ids_observed": len(track_ids_seen),
        "fps": fps,
        "width": info["width"],
        "height": info["height"],
        "duration_seconds": info["duration_seconds"],
    }
    
def create_event_clip(
    video_path,
    timestamp_seconds,
    output_path,
    window_seconds=3.0,
):
    """Create a short clip around a selected event timestamp."""
    from pathlib import Path
    import cv2

    if timestamp_seconds < 0:
        raise ValueError("Timestamp cannot be negative.")

    if window_seconds <= 0:
        raise ValueError("Window must be positive.")

    info = inspect_video(video_path)
    duration = info["duration_seconds"]

    if duration is None or duration <= 0:
        raise ValueError("Could not determine video duration.")

    if timestamp_seconds > duration:
        raise ValueError("Timestamp is beyond the end of the video.")

    start_time = max(0.0, timestamp_seconds - window_seconds)
    end_time = min(duration, timestamp_seconds + window_seconds)

    source = cv2.VideoCapture(str(video_path))
    if not source.isOpened():
        raise ValueError("Could not open source video.")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    fps = info["fps"] if info["fps"] > 0 else 30.0
    writer = cv2.VideoWriter(
        str(output),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (info["width"], info["height"]),
    )

    if not writer.isOpened():
        source.release()
        raise RuntimeError("Could not create event clip.")

    try:
        source.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)
        frames_to_read = max(1, int((end_time - start_time) * fps))
        frames_written = 0

        for _ in range(frames_to_read):
            ok, frame = source.read()
            if not ok:
                break
            writer.write(frame)
            frames_written += 1

        if frames_written == 0:
            raise ValueError("No frames could be read for the event clip.")

    finally:
        source.release()
        writer.release()

    return {
        "output_path": str(output),
        "start_seconds": start_time,
        "end_seconds": end_time,
        "frames_written": frames_written,
    }

