import base64
import json
import time

import requests
from requests import Response

from labcontrol.schema import (
    AWSAction,
    AWSContent,
    AWSContentFailure,
    AWSContentSuccess,
    AWSEnd,
    AWSEndFailure,
    AWSEndSuccess,
    AWSStart,
    AWSStartFailure,
    AWSStartSuccess,
    AWSStatus,
    AWSStatusFailure,
    AWSStatusSuccess,
    LabStatus,
    VocareumParams,
)

HEADERS = {
    "accept": "*/*",
    "accept-language": "es-419,es;q=0.9",
    "priority": "u=1, i",
    "sec-ch-ua": '"Not;A=Brand";v="24", "Chromium";v="128"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}


class VocareumApi:
    def __init__(self, params: VocareumParams):
        self.params = params

    def _make_request(self, action: AWSAction) -> Response:
        params = self.params.model_dump()
        params["a"] = action.value

        response = requests.get(
            url="https://labs.vocareum.com/util/vcput.php",
            params=params,
            headers=HEADERS,
        )
        return response

    def get_aws_status(self) -> AWSStatus:

        response = self._make_request(AWSAction.getawsstatus)

        if "failed" in response.text.lower():
            return AWSStatusFailure(success=False, error=response.text)
        if "lab status" in response.text.lower():
            text_with_br = response.text.split(":")[1].strip()
            status = text_with_br.replace("<br>", "")
            return AWSStatusSuccess(success=True, status=LabStatus(status))

        return AWSStatusFailure(success=False, error=response.text)

    def get_aws(self) -> AWSContent:
        self._wait_if_in_creation()

        response = self._make_request(AWSAction.getaws)
        if "<strong>Cloud Labs</strong>" in response.text:
            return AWSContentSuccess(success=True, content=response.text)
        return AWSContentFailure(success=False, error=response.text)

    def _wait_if_in_creation(self):
        result = self.get_aws_status()
        if result.success is False:
            raise Exception(f"Error getting AWS status: {result.error}")

        while result.status == LabStatus.in_creation:
            time.sleep(1)
            result = self.get_aws_status()
            if result.success is False:
                raise Exception(f"Error getting AWS status: {result.error}")

    def start_aws(self) -> AWSStart:
        self._wait_if_in_creation()

        response = self._make_request(AWSAction.startaws)
        if "success" in response.text:
            return AWSStartSuccess(success=True, content=json.loads(response.text))

        return AWSStartFailure(success=False, error=response.text)

    def end_aws(self) -> AWSEnd | AWSStatus:
        response = self._make_request(AWSAction.endaws)
        if "success" in response.text:
            return AWSEndSuccess(success=True, content=json.loads(response.text))

        return AWSEndFailure(success=False, error=response.text)

    def get_aws_sso(self, aws_sso: str) -> str:
        params = self.params.model_dump()
        params["a"] = AWSAction.ssodownloadaws.value

        data = {
            "a": "ssodownload",
            "data": aws_sso,
            "step": params["stepid"],
            "vockey": params["vockey"],
        }
        response = requests.post(
            "https://labs.vocareum.com/util/vcput.php", headers=HEADERS, data=data
        )

        response.raise_for_status()
        content_base64 = response.text.strip()

        content = base64.b64decode(content_base64)
        return content.decode("utf-8")
