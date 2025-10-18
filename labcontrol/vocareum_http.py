import requests
from requests import Response

from labcontrol.schema import (
    AWSAction,
    AWSStatus,
    AWSStatusFailure,
    AWSStatusSuccess,
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
        if "Lab status" in response.text.lower():
            return AWSStatusSuccess(success=True, status=response.text)

        return AWSStatusFailure(success=False, error=response.text)
