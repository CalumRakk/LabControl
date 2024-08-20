from pathlib import Path
from platform import system
from os import getenv
from enum import Enum

VOCAREUM_URL = "https://labs.vocareum.com/"
VOCAREUM_LOGIN_URL = "https://labs.vocareum.com/home/login.php"
AWSACADEMY_URL = "https://awsacademy.instructure.com"
AWSACADEMY_LOGIN_URL = "https://awsacademy.instructure.com/login/canvas"

PROJECT_NAME = "cloudAuto"
HOME = Path.home() / ".local/share" if system() == "Linux" else Path(getenv("APPDATA"))
PATH_COOKIES_BROWSER = HOME / PROJECT_NAME / "cookies_browser.json"
PATH_COOKIES = Path("cookies.json")

PATH_COOKIES_BROWSER.parent.mkdir(exist_ok=True, parents=True)


class BrowserStatus(Enum):
    Stopped = "Stopped"
    Running = "Running"
    Stopping = "Stopping"
    Unknown = "Unknown"

    @property
    def is_on(self) -> bool:
        return self in [BrowserStatus.Running]

    @property
    def is_off(self) -> bool:
        return not self in [BrowserStatus.Running]


class PCStatus(Enum):
    Stopped = "Stopped"
    Running = "Running"
    Stopping = "Stopping"
    Unknown = "Unknown"

    @property
    def is_on(self) -> bool:
        return self in [PCStatus.Running]

    @property
    def is_off(self) -> bool:
        return not self in [PCStatus.Running]
