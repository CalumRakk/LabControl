from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
import logging
from autoCloud.paquetes.aws.constants import BrowserStatus, PCStatus
from autoCloud.constants import ActionsInstance
from celery.result import AsyncResult
import redis
from . import utils
from autoCloud.paquetes.aws import Browser

from host.task import load_browser, browser_go_to_url

conn = redis.Redis(host="localhost", port=6379, db=0)

logger = logging.getLogger(__name__)


# def get_browser_status(request) -> HttpResponse:
#     logger.info("solicitud http get_browser_status")
#     browser_status = utils.get_browser_status()
#     data = {"browser_status": browser_status.translate}
#     json_data = json.dumps(data)
#     response = HttpResponse(json_data, content_type="application/json")
#     response["Access-Control-Allow-Origin"] = "*"
#     logger.info(f"respuesta http get_browser_status {json_data}")
#     return response

# def get_status(request) -> HttpResponse:
#     logger.info("solicitud http get_status")
#     browser_status = utils.get_browser_status()
#     pc_status = utils.get_pc_status()
#     data = {
#         "browser_status": browser_status.translate,
#         "pc_status": pc_status.translate,
#     }
#     # json_data = json.dumps(data)
#     # response = HttpResponse(json_data, content_type="application/json")
#     # response["Access-Control-Allow-Origin"] = "*"
#     return JsonResponse(data)
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response

class RedisDataView(APIView):
    def get(self, request):
        data = cache.get("status")
        if data:
            return Response(data)
        return Response({"error": "Data not found"}, status=404)


def browser_control(request):
    try:
        status = json.loads(conn.get("status").decode("utf-8"))
        browser_status = getattr(BrowserStatus, status["browser_status"])

        data = json.loads(request.body)
        action = data.get("action")
        if action == ActionsInstance.Start.value:
            logger.info("action stop")
            load_browser.delay()
            status["browser_status"] = BrowserStatus.Running.value
        elif action == "go_to_url":
            url = data.get("url")
            browser_go_to_url.delay(url)

        conn.set("status", json.dumps(status))
        return JsonResponse(status, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Formato JSON inválido"}, status=400)


def aws(request) -> HttpResponse:
    # try:
    #     if request.method == "POST":
    #         try:
    #             body = json.loads(request.body)
    #         except json.JSONDecodeError:
    #             pass

    #         if body["a"] == "turnOnBrowser":
    #             logger.info("action turnOnBrowser")
    #             load_browser.delay()
    #             return "loading browser"
    # except:
    #     pass

    logger.info("solicitud http get aws")

    return render(
        request,
        "host/index.html",
        {},
    )
