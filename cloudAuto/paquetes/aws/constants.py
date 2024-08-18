from pathlib import Path
from platform import system
from os import getenv
from enum import Enum

# "North Virginia"
AWS_EAST_1_URL = (
    "https://us-east-1.console.aws.amazon.com/console/home?region=us-east-1#"
)
# "Oregon"
_AWS_WEST_2_URL = (
    "https://us-west-2.console.aws.amazon.com/console/home?region=us-west-2#"
)

AWS_WEST_2_INSTANCES_URL = (
    "https://us-west-2.console.aws.amazon.com/ec2/home?region=us-west-2#Instances:"
)

INSTANCE_NAME = "Server upgrade"
INSTANCE_ID = "i-0263a4411abc36d39"
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

VOCAREUM_URL = "https://labs.vocareum.com/"
VOCAREUM_LOGIN_URL = "https://labs.vocareum.com/home/login.php"
AWSACADEMY_URL = "https://awsacademy.instructure.com"
AWSACADEMY_LOGIN_URL = "https://awsacademy.instructure.com/login/canvas"

PROJECT_NAME = "autoCloud"
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
