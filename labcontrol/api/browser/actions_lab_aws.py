from typing import List, cast
from selenium.webdriver import Chrome
import logging
from labcontrol.api.parser import SeleniumCookie
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
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

def get_course_id(driver):
    try:
        clickable_course= WebDriverWait(driver, 10).until(EC.element_to_be_clickable(("xpath",f".//a[@class='ic-DashboardCard__link']")))
        href= cast(str, clickable_course.get_attribute("href"))
        return href.split("/")[-1]        
    except TimeoutException:
        logger.error("TimeoutException: No se pudo encontrar el elemento clickeable.")
        return False
def get_lab_item_id(driver):
    try:
        clickable_element= WebDriverWait(driver, 10).until(EC.element_to_be_clickable(("xpath",f".//ul[@class='ig-list items context_module_items ' and count(child::*) = 1]/li//a")))
        href= cast(str, clickable_element.get_attribute("href"))
        return href.split("/")[-1]        
    except TimeoutException:
        logger.error("TimeoutException: No se pudo encontrar el elemento clickeable.")
        return False