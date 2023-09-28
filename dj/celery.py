# celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dj.settings')

app = Celery('dj')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    print('SETUP DONE')
    from app.tasks import refresh_tokens
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(
        crontab(hour=24), refresh_tokens.s()
        # 10, refresh_tokens.s()
    )
