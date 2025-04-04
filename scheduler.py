from apscheduler.schedulers.background import BackgroundScheduler
from db import get_today_revisions

def check_revisions():
    revisions = get_today_revisions()
    if revisions:
        print("📢 Reminder: Revise these topics today!", [r['topic'] for r in revisions])

scheduler = BackgroundScheduler()
scheduler.add_job(check_revisions, 'interval', days=1)
scheduler.start()
