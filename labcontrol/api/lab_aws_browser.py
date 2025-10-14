import logging
import time
from pathlib import Path
from typing import List, Literal, Optional, Union

import requests

from labcontrol.api.browser.actions_lab_aws import set_cookies_on_driver
from labcontrol.api.browser.driver import DriverManager
from labcontrol.api.parser import SeleniumCookie
from labcontrol.api.browser.actions_lab_aws import get_course_id, get_lab_item_id, get_lab_item_id, set_cookies_on_driver

logger = logging.getLogger(__name__)

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'es',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'referer': 'https://awsacademy.instructure.com/login/canvas',
    'sec-ch-ua': '"Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',
}


class LabAWSBrowserAPI:
    """Usa Selenium para scroll y extracción con cursor."""

    def __init__(
        self, chrome_profile: Optional[Union[str, Path]] = None, headless=False
    ):
        logger.info("Inicializando TiktokBrowserAPI con Selenium.")
        self.browser = DriverManager(chrome_profile, headless)

    def set_cookies(self, cookies: List[SeleniumCookie]):
        logger.info("Estableciendo cookies en el navegador.")
        set_cookies_on_driver(self.browser.driver, cookies)

    def go_to_lab_home(self):
        driver= self.browser.driver

        course_id= get_course_id(driver)

        url_module= f"https://awsacademy.instructure.com/courses/{course_id}/modules"

        driver.get(url_module)

        lab_item_id= get_lab_item_id(driver)

        url_lab= f"https://awsacademy.instructure.com/courses/{course_id}/modules/items/{lab_item_id}"

        driver.get(url_lab)