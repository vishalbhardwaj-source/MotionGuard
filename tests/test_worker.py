import time
from pathlib import Path
from src.worker import submit_video_job, get_job_status, list_jobs


def test_worker_job_status_unknown():
    assert get_job_status("NON_EXISTENT") is None


def test_worker_submission_invalid_video(tmp_path):
    fake_video = tmp_path / "does_not_exist.mp4"
    fake_out = tmp_path / "out.mp4"

    job_id = submit_video_job(str(fake_video), str(fake_out))
    assert job_id.startswith("JOB-")

    # Wait briefly for worker to register failure
    time.sleep(0.3)
    status = get_job_status(job_id)
    assert status is not None
    assert status["status"] in ("QUEUED", "RUNNING", "FAILED")
