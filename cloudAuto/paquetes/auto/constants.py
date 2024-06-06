from pathlib import Path
from platform import system
from os import getenv
from enum import Enum

URL_GETAWS = "https://labs.vocareum.com/util/vcput.php"
URL_LOGIN = "https://awsacademy.instructure.com/login/canvas"
URL_LAB = "https://awsacademy.instructure.com/courses/51160/modules/items/5197438"
PROJECT_NAME = "cloudAuto"
HOME = Path.home() / ".local/share" if system() == "Linux" else Path(getenv("APPDATA"))
PATH_COOKIES_BROWSER = HOME / PROJECT_NAME / "cookies_browser.json"
PATH_COOKIES = Path("cookies.json")
PATH_USER = Path("user")


HEADERS = {
    "authority": "labs.vocareum.com",
    "accept": "*/*",
    "accept-language": "es,es-ES;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "referer": "https://labs.vocareum.com/main/main.php?m=clabide&mode=s&asnid=1899604&stepid=1899605&hideNavBar=1",
    "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
    "x-requested-with": "XMLHttpRequest",
}

PARAMS_GETAWS = {
    "a": "getaws",
    "type": "1",
    "stepid": "1899605",
    "version": "0",
    "v": "0",
    "vockey": "3h2zju23ZCRfHzOqtarKDA==",
}

PARAMS_STARTAWS = {
    "a": "startaws",
    "stepid": "1899605",
    "version": "0",
    "mode": "s",
    "type": "1",
    "vockey": "3h2zju23ZCRfHzOqtarKDA==",
}

REQUIRED_COOKIE_KEYS = [
    "vocareum_entry_link",
    "PHPSESSID",
    "logintoken",
    "tokenExpire",
    "usertoken",
    "userid",
    "t2fausers",
    "usingLTI",
    "myfolder",
    "currentcourse",
    "currentassignment",
    "userassignment",
]

REQUIRED_COOKIE_FOR_DescribeInstances = [
    "amz-sdk-invocation-id",
    "amz-sdk-request",
    "authorization",
    "content-type",
    "sec-ch-ua",
    "sec-ch-ua-mobile",
    "sec-ch-ua-platform",
    "x-amz-content-sha256",
    "x-amz-date",
    "x-amz-security-token",
    "x-amz-user-agent",
]


PATH_COOKIES_BROWSER.parent.mkdir(exist_ok=True, parents=True)
Status_check = [
    "Initializing",
]


class StatusInstance(Enum):
    Stopped = "Stopped"
    Pending = "Pending"
    Running = "Running"
    Stopping = "Stopping"

    @property
    def is_on(self) -> bool:
        return self in (StatusInstance.Running)

    @property
    def is_off(self) -> bool:
        return not self in (StatusInstance.Running)


# class ActionsInstance(Enum):
#     Stop = "Start instance"
#     Start = "Stop instance"
#     Reboot = "Reboot instance"
#     Hibernate = "Hibernate instance"
class ActionsInstance(Enum):
    Stop = "item-1"
    Start = "item-2"
    Reboot = "item-3"
    Hibernate = "item-4"


STATUS_SPANISH = {
    "Detenida": StatusInstance.Stopped,
    "Pendiente": StatusInstance.Pending,
    "En ejecución": StatusInstance.Running,
    "Deteniéndose": StatusInstance.Stopping,
}
