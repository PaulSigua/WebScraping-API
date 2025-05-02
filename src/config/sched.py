# sched.py
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from ws_freshportal.main import sched_freshportal
from ws_unosof.main import scheduler_unosof

scheduler = BackgroundScheduler()

def execute_all_tasks():
    sched_freshportal()
    scheduler_unosof()

def start_scheduler():
    scheduler.add_job(execute_all_tasks, 'cron', hour=3, minute=0)
    scheduler.start()
    atexit.register(scheduler.shutdown)
