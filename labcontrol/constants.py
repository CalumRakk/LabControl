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

LOGIN_AGAIN_MESSAGE = "Please login again"

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


VOCAREUM_VCPU_URL = "https://labs.vocareum.com/util/vcput.php"


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


class LabStatus(Enum):
    stopped = "stopped"
    stopping = "stopping"
    in_creation = "in creation"
    ready = "ready"


class AWSAction(Enum):
    getaws = "getaws"
    startaws = "startaws"  # Sustituye "otheraction" con el otro valor que necesites
    getawsstatus = "getawsstatus"
    endaws = "endaws"


LAB_NOT_STARTED = "Lab status: not started"


# Acciones relacionadas con al panel lab de AWS Academy
class ActionsInstance(Enum):
    Stop = "Stop"
    Start = "Start"
    Reboot = "Reboot"
    Hibernate = "Hibernate"

    @property
    def translate(self) -> str:
        return ACTIONS_SPANISH[self]

    @property
    def item(self) -> str:
        return ACTIONS_ITEMS[self]


ACTIONS_ITEMS = {
    ActionsInstance.Stop: "item-1",
    ActionsInstance.Start: "item-2",
    ActionsInstance.Reboot: "item-3",
    ActionsInstance.Hibernate: "item-4",
}

ACTIONS_SPANISH = {
    ActionsInstance.Stop: "Detener",
    ActionsInstance.Start: "Iniciar",
    ActionsInstance.Reboot: "Reiniciar",
    ActionsInstance.Hibernate: "Hibernar",
}


class Action(Enum):
    startBrowser = "startBrowser"
    startServerMinecraft = "startServerMinecraft"
    stopBrowser = "stopBrowser"
    stopServerMinecraft = "stopServerMinecraft"
    go_to_url = "go_to_url"
    checkTask = "checkTask"
    getStatus = "getStatus"


class StatusInstance(Enum):
    Stopped = "Stopped"
    Pending = "Pending"
    Running = "Running"
    Stopping = "Stopping"

    @property
    def is_on(self) -> bool:
        return self in [StatusInstance.Running]

    @property
    def is_off(self) -> bool:
        return not self in [StatusInstance.Running]

    @property
    def translate(self) -> str:
        return STATUS_SPANISH[self]


class StatusLab(Enum):
    Terminated = "Terminated"
    Initializing = "Initializing"
    In_Creation = "In Creation"
    Ready = "Ready"
    Shutting_down = "Shutting down"

    @property
    def is_on(self) -> bool:
        return self in [StatusLab.Ready]

    @property
    def is_off(self) -> bool:
        return not self in [StatusLab.Ready]

    @property
    def translate(self) -> str:
        return STATUS_LAB_SPANISH[self]

    @classmethod
    def string_to_status(cls, status: str) -> "StatusLab":
        if hasattr(cls, status):
            return getattr(cls, status)

        if status == "Creation":
            return StatusLab.In_Creation
        elif status == "down":
            return StatusLab.Terminated

        raise Exception(f"status {status} not found")


STATUS_SPANISH = {
    StatusInstance.Stopped: "Detenida",
    StatusInstance.Pending: "Pendiente",
    StatusInstance.Running: "En ejecución",
    StatusInstance.Stopping: "Deteniéndose",
}

STATUS_LAB_SPANISH = {
    StatusLab.Terminated: "Terminada",
    StatusLab.Initializing: "Iniciando",
    StatusLab.In_Creation: "En Creación",
    StatusLab.Ready: "Listo",
    StatusLab.Shutting_down: "Apagando",
}
