# Create your tasks here
from celery import shared_task
import json

from autoCloud.paquetes.aws import Browser
from autoCloud.paquetes.aws.constants import BrowserStatus, PCStatus
import redis
from django.core.cache import cache

# conn = redis.Redis(host="localhost", port=6379, db=0)

# # Inializando la base de datos con la configuración inicial
# status = {
#     "browser_status": BrowserStatus.Unknown.value,
#     "pc_status": PCStatus.Unknown.value,
# }
# conn.set("status", json.dumps(status))


@shared_task
def load_browser():
    browser = Browser()
    browser.go_url("https://www.google.com")
    
@shared_task
def browser_go_to_url(url):
    browser = Browser()
    browser.go_url(url)