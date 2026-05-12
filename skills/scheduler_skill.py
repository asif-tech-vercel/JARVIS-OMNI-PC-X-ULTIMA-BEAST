"""JARVIS Scheduler Skill - Task scheduling."""

import json
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from jarvis_core.logger import get_logger

logger = get_logger()

scheduler = BackgroundScheduler()

def schedule_task(command: str, trigger: str = "date", **kwargs) -> dict:
    """Schedule a task."""
    try:
        job = scheduler.add_job(
            lambda: _run_task(command),
            trigger,
            **kwargs
        )
        logger.action(f"Scheduled: {command}", "SUCCESS", "medium")
        return {"success": True, "job_id": job.id}
    except Exception as e:
        return {"success": False, "error": str(e)}

def _run_task(command: str):
    logger.info(f"Running scheduled: {command}")

def list_scheduled() -> list:
    return [{"id": j.id, "next": str(j.next_run_time)} for j in scheduler.get_jobs()]

def cancel_scheduled(job_id: str) -> dict:
    try:
        scheduler.remove_job(job_id)
        return {"success": True}
    except: return {"success": False, "error": "Job not found"}

def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")