# Create your tasks here
from celery import shared_task
import json

from cloudAuto.paquetes.aws import Browser
from cloudAuto.paquetes.aws.constants import BrowserStatus, PCStatus
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
def start_browser():
    browser = Browser()
    if browser.status == BrowserStatus.Stopped:
        cache.set("browser_status", BrowserStatus.Running.value)

    stop_browser.apply_async(countdown=10)
    browser.load_aws()
    return True


@shared_task
def stop_browser():
    browser = Browser()
    Browser.stop(browser)
    return True


@shared_task
def go_to_url(url):
    browser = Browser()
    browser.go_url(url)
    stop_browser.apply_async(countdown=10)
    return True


@shared_task
def get_status():
    browser = Browser()

    return {"browser_status": browser.status.value, "pc_status": None}
