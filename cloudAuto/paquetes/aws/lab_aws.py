import logging

from lxml import etree
import vcr

from cloudAuto import log_decorator
from . import lab_aws_utils
from .lab_aws_utils import login_decorator
from .constants import LAB_NOT_STARTED

logger = logging.getLogger(__name__)


class LabAWS:
    @log_decorator
    @login_decorator
    def getaws(self) -> dict:

        path_data, path_cookies = lab_aws_utils.load_paths()
        if not path_cookies.exists() or not path_data.exists():
            return {"data": None, "error": "Files not found"}

        data, cookies = lab_aws_utils.load_data_and_cookies(path_data, path_cookies)
        response = lab_aws_utils.make_request_get_aws(data, cookies)

        root = etree.fromstring(response.text, etree.HTMLParser())
        content = "".join([text for text in root.find(".//body").itertext()])
        msg_error = lab_aws_utils.parse_error(root)
        if msg_error:
            return {"data": None, "error": msg_error}

        if content == LAB_NOT_STARTED:
            return {"data": LAB_NOT_STARTED, "error": None}

        status = lab_aws_utils.extract_status(root)
        sessiones = lab_aws_utils.extract_session_times(content, status)
        expiretime = lab_aws_utils.get_expire_time(root)
        return {
            "data": {
                "status": status,
                "sessions": sessiones,
                "expiretime": expiretime,
            },
            "error": None,
        }
