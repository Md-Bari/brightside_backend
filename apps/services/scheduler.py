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


def run_weekly_website_scrape(interval_seconds: int = 604800):
    """
    Background loop that scrapes https://bright-carwash-website.vercel.app/
    and updates the Knowledge Base every 1 week (604,800 seconds).
    """
    from apps.knowledgebase.scraper import WebsiteScraperService

    logger.info("Weekly website scraper background thread started (Interval: %d seconds / 1 week).", interval_seconds)
    scraper = WebsiteScraperService()

    # Initial scrape execution on server startup
    try:
        logger.info("Triggering initial website scrape for Knowledge Base...")
        res = scraper.scrape_and_update_kb()
        logger.info("Initial website scrape result: %s", res)
    except Exception as exc:
        logger.error("Initial website scrape error: %s", exc)

    while True:
        try:
            time.sleep(interval_seconds)
            logger.info("Triggering scheduled weekly website scrape...")
            res = scraper.scrape_and_update_kb()
            logger.info("Scheduled weekly website scrape result: %s", res)
        except Exception as exc:
            logger.error("Error during scheduled weekly website scrape: %s", exc)


def start_service_scheduler(interval_seconds: int = 28800):
    """
    Starts the periodic sync loop & weekly scraper loop in background daemon threads.
    Guarantees thread-safe single initialization.
    """
    global _scheduler_started
    with _scheduler_lock:
        if _scheduler_started:
            return

        # 1. 8-Hour Service Sync Thread
        service_thread = threading.Thread(
            target=run_periodic_sync,
            args=(interval_seconds,),
            daemon=True,
            name="ServiceSyncSchedulerThread"
        )
        service_thread.start()

        # 2. 1-Week Website Scraper KB Thread (604,800 seconds)
        scraper_thread = threading.Thread(
            target=run_weekly_website_scrape,
            args=(604800,),
            daemon=True,
            name="WebsiteScraperSchedulerThread"
        )
        scraper_thread.start()

        _scheduler_started = True
        logger.info("Schedulers (8-hour Service Sync & 1-week Website KB Scraper) initialized and running.")

