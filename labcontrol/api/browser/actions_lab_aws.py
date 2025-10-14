from selenium.webdriver import Chrome
import logging
from labcontrol.api.lab_aws_browser import List
from labcontrol.api.parser import SeleniumCookie

logger = logging.getLogger(__name__)

    
def set_cookies_on_driver(
    driver: Chrome, cookies: List[SeleniumCookie]
):
    pass