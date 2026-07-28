"""
Background Scheduler for Periodic Service & Location Synchronization.
Runs every 8 hours (28,800 seconds) in a background thread.
"""
import time
import threading
import logging

logger = logging.getLogger("brightside")
_scheduler_started = False
_scheduler_lock = threading.Lock()


def run_periodic_sync(interval_seconds: int = 28800):
    """
    Background loop that runs ServiceSyncService.sync_all() every interval_seconds.
    Default interval is 28,800 seconds (8 hours).
    """
    from .services import ServiceSyncService

    logger.info("Service sync background scheduler started (Interval: %d seconds / 8 hours).", interval_seconds)
    sync_service = ServiceSyncService()

    # Initial sync execution
    try:
        logger.info("Triggering initial service synchronization...")
        res = sync_service.sync_all()
        logger.info("Initial service synchronization result: %s", res)
    except Exception as exc:
        logger.error("Initial service synchronization error: %s", exc)

    while True:
        try:
            time.sleep(interval_seconds)
            logger.info("Triggering scheduled 8-hour service synchronization...")
            res = sync_service.sync_all()
            logger.info("Scheduled service synchronization result: %s", res)
        except Exception as exc:
            logger.error("Error during scheduled service synchronization: %s", exc)


def start_service_scheduler(interval_seconds: int = 28800):
    """
    Starts the periodic sync loop in a background daemon thread.
    Guarantees thread-safe single initialization.
    """
    global _scheduler_started
    with _scheduler_lock:
        if _scheduler_started:
            return
        thread = threading.Thread(
            target=run_periodic_sync,
            args=(interval_seconds,),
            daemon=True,
            name="ServiceSyncSchedulerThread"
        )
        thread.start()
        _scheduler_started = True
        logger.info("ServiceSyncSchedulerThread initialized and running in background.")
