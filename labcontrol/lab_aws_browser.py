import logging
import time
from pathlib import Path
from typing import List, Literal, Optional, Union

import requests

from labcontrol.browser.actions_lab_aws import get_lab_aws_details, set_cookies_on_driver, switch_to_iframe, wait_for_lab_load
from labcontrol.browser.driver import DriverManager
from labcontrol.parser import SeleniumCookie, parse_lab_aws_details_content
from labcontrol.browser.actions_lab_aws import get_course_id, get_lab_item_id, get_lab_item_id, set_cookies_on_driver

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
        self, cookies: Optional[List[SeleniumCookie]]=None, chrome_profile: Optional[Union[str, Path]] = None, headless=False
    ):
        """Inicializa la API del navegador de laboratorios AWS Academy.
        
        Args:
            cookies (Optional[List[SeleniumCookie]], optional): Cookies para iniciar sesión. Defaults to None.
            chrome_profile (Optional[Union[str, Path]], optional): Ruta al perfil de Chrome. Defaults to None.
            headless (bool, optional): Ejecutar en modo headless. Defaults to False.
        
        Nota: Si se proporcionan cookies, se establecerán en el navegador y se navegará a la página principal del laboratorio.
        
        """
        logger.info("Inicializando LabAWSBrowserAPI con Selenium.")
        self.browser = DriverManager(chrome_profile, headless)

        if cookies:
            self._set_cookies(cookies)
            self._go_to_lab_home()

    def _set_cookies(self, cookies: List[SeleniumCookie]):
        logger.info("Estableciendo cookies en el navegador.")
        set_cookies_on_driver(self.browser.driver, cookies)

    @property
    def is_in_lab(self) -> bool:
        current_url= self.browser.driver.current_url
        return "courses" in current_url and "items" in current_url
    def _get_url_lab(self):
        driver= self.browser.driver

        course_id= get_course_id(driver)

        url_module= f"https://awsacademy.instructure.com/courses/{course_id}/modules"

        driver.get(url_module)

        lab_item_id= get_lab_item_id(driver)

        return f"https://awsacademy.instructure.com/courses/{course_id}/modules/items/{lab_item_id}"
    def _go_to_lab_home(self):
        if self.is_in_lab:
            return True
        
        url_lab= self._get_url_lab()
        self.browser.driver.get(url_lab)
        wait_for_lab_load(self.browser.driver)
        logger.info("¡Laboratorio cargado exitosamente!")
        return True
    
    def get_lab_details(self):
        content_lan= get_lab_aws_details(self.browser.driver)
        return parse_lab_aws_details_content(content_lan)

    def get_cookies_vocareum(self)->List[SeleniumCookie]:
        with switch_to_iframe(self.browser.driver, 10):
            return self.browser.driver.get_cookies()