from typing import List
from selenium.webdriver import Chrome
import logging
from labcontrol.api.parser import SeleniumCookie

logger = logging.getLogger(__name__)

    
def set_cookies_on_driver(
    driver: Chrome, cookies: List[SeleniumCookie]
):
    url= "https://awsacademy.instructure.com/404"
    driver.get(url)

    driver.delete_all_cookies()

    for cookie in cookies:
        # Expires/Max-Age en set-cookies tiene el valor 'Session', lo que parece indicar una session sin expiracion o hasta que se cierre el navegador. Selenium no acepta ese valor, por lo que se elimina y se logra un funcionamiento similar al navegador.
        cookie.pop("expiry") 
        driver.add_cookie(cookie)

    driver.get("https://awsacademy.instructure.com")