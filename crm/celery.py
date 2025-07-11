import os
import sys
from celery import Celery
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')

app = Celery('alx_travel_app', broker='amqp://root:root@localhost:5672/myvhost')  #Use Env Variables for production

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()