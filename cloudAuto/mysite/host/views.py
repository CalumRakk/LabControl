from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
from autoCloud.paquetes.aws import Browser
from autoCloud import Config
from autoCloud.constants import ActionsInstance, StatusInstance
import time
from . import utils
import logging


logger = logging.getLogger(__name__)


def get_browser_status(request) -> HttpResponse:
    logger.info("solicitud http get_browser_status")
    browser_status = utils.get_browser_status()
    data = {"browser_status": browser_status.translate}
    json_data = json.dumps(data)
    response = HttpResponse(json_data, content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    logger.info(f"respuesta http get_browser_status {json_data}")
    return response


def get_pc_status(request) -> HttpResponse:
    logger.info("solicitud http get_pc_status")
    pc_status = utils.get_pc_status()
    data = {"pc_status": pc_status.translate}
    json_data = json.dumps(data)
    response = HttpResponse(json_data, content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    return response


def get_status(request) -> HttpResponse:
    logger.info("solicitud http get_status")
    browser_status = utils.get_browser_status()
    pc_status = utils.get_pc_status()
    data = {
        "browser_status": browser_status.translate,
        "pc_status": pc_status.translate,
    }
    # json_data = json.dumps(data)
    # response = HttpResponse(json_data, content_type="application/json")
    # response["Access-Control-Allow-Origin"] = "*"
    return JsonResponse(data)


def aws(request) -> HttpResponse:
    try:
        if request.method == "POST":
            logger.info("solicitud http post aws")
            browser_status = utils.get_browser_status()
            try:
                body = json.loads(request.body)
            except json.JSONDecodeError:
                return HttpResponseBadRequest("Invalid JSON")

            if body["a"] == "turnOnBrowser":
                logger.info("action turnOnBrowser")
                if browser_status.is_off:
                    browser = Browser()
                    lab = browser.load_aws(cache=True)

                return utils.get_status(http_response=True)

            elif body["a"] == "turnOnPC":
                logger.info("action turnOnPC")

                value = body["value"]
                pc_status = utils.get_pc_status()
                if isinstance(pc_status, StatusInstance):
                    if pc_status.is_on and value:
                        utils.set_action(ActionsInstance.Start)
                    elif pc_status.is_on and value is False:
                        utils.set_action(ActionsInstance.Stop)
                    return HttpResponse(status=204)
    except:
        pass

    logger.info("solicitud http get aws")
    return render(
        request,
        "host/index.html",
        {},
    )
