import json
import logging
from autoCloud.paquetes.aws import Browser
from autoCloud import Config
from autoCloud.constants import ActionsInstance, StatusInstance
from django.http import HttpResponse, HttpResponseBadRequest

logging.basicConfig(
    filename="log.txt",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%m-%Y %I:%M:%S %p",
    level=logging.INFO,
    encoding="utf-8",
)
logger = logging.getLogger(__name__)


def get_browser_status() -> StatusInstance:
    browser = Browser()
    status = browser.status
    logger.info(f"browser_status: {status}")
    return status


def set_action(action: ActionsInstance):
    config = Config()
    browser = Browser()
    browser_status = get_browser_status()
    if browser_status.is_on:
        lab_page = browser.load_aws(cache=True)
        instance_id = config["instance_id"]["server_double"]
        # browser.set_action_instance(lab_page, instance_id, action)


def get_pc_status() -> StatusInstance:
    config = Config()
    browser_status = get_browser_status()

    if browser_status.is_on:
        browser = Browser()
        lab_page = browser.load_aws(cache=True)
        instance_id = config["instance_id"]["server_double"]
        pc_status = browser.get_status_instance(lab_page, instance_id)
        logger.info(f"pc_status: {pc_status}")
        return pc_status
    return StatusInstance.Unknown


def get_status(http_response=False) -> dict:
    browser_status = get_browser_status()
    pc_status = get_pc_status()

    if http_response:
        data = {
            "browser_status": browser_status.translate,
            "pc_status": pc_status.translate,
        }
        json_data = json.dumps(data)
        response = HttpResponse(json_data, content_type="application/json")
        response["Access-Control-Allow-Origin"] = "*"
        return response

    data = {
        "browser_status": browser_status,
        "pc_status": pc_status,
    }
    return data
