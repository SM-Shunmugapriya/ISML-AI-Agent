from apscheduler.schedulers.background import BackgroundScheduler

from services.freshness_checker import verify_top_resources


scheduler = BackgroundScheduler(timezone="Asia/Kolkata")


def start_freshness_scheduler():
    if scheduler.running:
        return

    scheduler.add_job(
        verify_top_resources,
        trigger="cron",
        hour=2,
        minute=0,
        id="daily_resource_freshness_check",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()
    print("Freshness scheduler started. Daily verification: 2:00 AM IST.")


def stop_freshness_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
