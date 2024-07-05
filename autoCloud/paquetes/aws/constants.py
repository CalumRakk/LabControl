from pathlib import Path
from platform import system
from os import getenv

# "North Virginia"
URL_AWS_EAST_1 = (
    "https://us-east-1.console.aws.amazon.com/console/home?region=us-east-1#"
)
# "Oregon"
URL_AWS_WEST_2 = (
    "https://us-west-2.console.aws.amazon.com/console/home?region=us-west-2#"
)

URL_AWS_WEST_2_INSTANCES = (
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