import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "skeleton.settings")

app = Celery("skeleton")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


app.conf.task_acks_late = True
app.conf.task_queue_max_priority = 10
app.conf.task_default_priority = 5
app.conf.worker_concurrency = 1
app.conf.worker_prefetch_multiplier = 1
app.conf.task_serializer = "json"
app.conf.result_serializer = "json"
app.conf.result_backend_transport_options = {"global_keyprefix": "celery_result_"}
app.conf.beat_schedule = {
    # "remove-orphaned-files-daily": {
    #     "task": "apps.orphan_files_cleaner.tasks.scan_and_remove_orphaned_files",
    #     "schedule": 60 * 60 * 24,
    #     "args": (),
    # },
    "cleanup-otp-daily": {
        "task": "apps.accounts.tasks.cleanup_expired_otp_requests",
        "schedule": crontab(hour=3, minute=0),
    },
    "cleanup_inactive_users": {
        "task": "apps.accounts.tasks.cleanup_inactive_users",
        "schedule": crontab(hour=4, minute=0),
    },
}
