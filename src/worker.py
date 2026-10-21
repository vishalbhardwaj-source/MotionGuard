import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4

from src.video_processor import track_video

# Single worker pool for background video processing
_EXECUTOR = ThreadPoolExecutor(max_workers=2)
_JOBS = {}
_JOBS_LOCK = threading.Lock()


def submit_video_job(
    video_path,
    output_path,
    trajectory_output_path=None,
    confidence=0.25,
    imgsz=640,
    frame_skip=0,
    classes=(2, 3, 5, 7),
    tracker="bytetrack.yaml",
):
    """
    Submit a video tracking task to the background worker pool.
    Returns a unique job_id for non-blocking status polling.
    """
    job_id = f"JOB-{uuid4().hex[:8].upper()}"

    with _JOBS_LOCK:
        _JOBS[job_id] = {
            "job_id": job_id,
            "status": "QUEUED",
            "progress": 0.0,
            "submitted_at": time.time(),
            "completed_at": None,
            "result": None,
            "error": None,
            "video_path": str(video_path),
            "output_path": str(output_path),
        }

    def _worker():
        with _JOBS_LOCK:
            _JOBS[job_id]["status"] = "RUNNING"

        def _on_progress(p):
            with _JOBS_LOCK:
                _JOBS[job_id]["progress"] = round(p, 3)

        try:
            res = track_video(
                video_path=video_path,
                output_path=output_path,
                trajectory_output_path=trajectory_output_path,
                progress_callback=_on_progress,
                confidence=confidence,
                imgsz=imgsz,
                frame_skip=frame_skip,
                classes=classes,
                tracker=tracker,
            )
            with _JOBS_LOCK:
                _JOBS[job_id]["status"] = "COMPLETED"
                _JOBS[job_id]["progress"] = 1.0
                _JOBS[job_id]["completed_at"] = time.time()
                _JOBS[job_id]["result"] = res
        except Exception as exc:
            with _JOBS_LOCK:
                _JOBS[job_id]["status"] = "FAILED"
                _JOBS[job_id]["completed_at"] = time.time()
                _JOBS[job_id]["error"] = str(exc)

    _EXECUTOR.submit(_worker)
    return job_id


def get_job_status(job_id):
    """Get the current progress and status of a background video processing job."""
    with _JOBS_LOCK:
        job = _JOBS.get(job_id)
        return dict(job) if job else None


def list_jobs():
    """List all submitted background jobs."""
    with _JOBS_LOCK:
        return [dict(j) for j in _JOBS.values()]
