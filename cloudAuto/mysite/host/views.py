from django.shortcuts import render
from django.http import HttpResponse
import json
from autoCloud.paquetes.aws import Browser
from autoCloud import Config
from autoCloud.constants import ActionsInstance, StatusInstance
import time


def get_browser_status() -> StatusInstance:
    browser = Browser()
    return browser.status


def browser_status(request):
    browser_status = get_browser_status()
    data = {"browser_status": browser_status.translate}
    json_data = json.dumps(data)
    response = HttpResponse(json_data, content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    return response


def aws(request):
    if request.method == "POST":
        browser_status = get_browser_status()
        if browser_status.is_off:
            browser = Browser()
            browser.status = StatusInstance.Pending
            browser.load_aws(cache=True)
            browser.status = StatusInstance.Running
        return HttpResponse(status=204)

    # Envía una respuesta al cliente
    status = get_browser_status()
    return render(
        request,
        "host/index.html",
        {"browser_status": status, "Status": StatusInstance.__members__},
    )
