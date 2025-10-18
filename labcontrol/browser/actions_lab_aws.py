import logging
from contextlib import contextmanager
from typing import List, cast

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from labcontrol.browser.utils import clear_content
from labcontrol.parser import SeleniumCookie

logger = logging.getLogger(__name__)


def set_cookies_on_driver(driver: Chrome, cookies: List[SeleniumCookie]):
    url = "https://awsacademy.instructure.com/404"
    driver.get(url)

    driver.delete_all_cookies()

    for cookie in cookies:
        cookie_dict = cookie.model_dump()

        if cookie_dict.get("expiry", 0) == 0:
            cookie_dict.pop("expiry")

        driver.add_cookie(cookie_dict)

    driver.get("https://awsacademy.instructure.com")


def get_course_id(driver):
    try:
        wait = WebDriverWait(driver, 10)
        clickable_course = wait.until(
            EC.element_to_be_clickable(
                ("xpath", f".//a[@class='ic-DashboardCard__link']")
            )
        )
        href = cast(str, clickable_course.get_attribute("href"))
        return href.split("/")[-1]
    except TimeoutException:
        logger.error("TimeoutException: No se pudo encontrar el elemento clickeable.")
        return False


def get_lab_item_id(driver):
    try:
        clickable_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    "xpath",
                    f".//ul[@class='ig-list items context_module_items ' and count(child::*) = 1]/li//a",
                )
            )
        )
        href = cast(str, clickable_element.get_attribute("href"))
        return href.split("/")[-1]
    except TimeoutException:
        logger.error("TimeoutException: No se pudo encontrar el elemento clickeable.")
        return False


@contextmanager
def switch_to_iframe(driver: Chrome, timeout: int = 30):
    try:
        wait = WebDriverWait(driver, timeout)
        iframe = wait.until(
            EC.frame_to_be_available_and_switch_to_it(
                ("xpath", f".//iframe[@src='about:blank' and @class='tool_launch']")
            )
        )
        yield True
    except TimeoutException as e:
        logger.error("TimeoutException: No se pudo encontrar el iframe.")
        return False
    finally:
        driver.switch_to.default_content()


def wait_for_lab_load(driver: Chrome, timeout: int = 30):
    try:

        with switch_to_iframe(driver, timeout):
            wait = WebDriverWait(driver, timeout)
            elemento_dentro = wait.until(
                EC.element_to_be_clickable(("id", "launchclabsbtn"))
            )

            logger.info(
                f"¡Contenido del iframe cargado! Elemento encontrado: {elemento_dentro.get_attribute('onclick')}"
            )
            return True

    except TimeoutException:
        logger.info("El iframe no cargó en 10 segundos. Verifica la conexión o el ID.")
        return False


def get_lab_aws_details(driver: Chrome) -> list[str]:
    with switch_to_iframe(driver):
        aws_details_element = driver.find_element("id", "detailbtn2")
        aws_details_element.click()

        wait = WebDriverWait(driver, 10)
        aws_details_content = wait.until(
            EC.presence_of_element_located(("id", "awsdetailsframe"))
        )

        content = cast(str, aws_details_content.get_attribute("innerHTML"))

        content_lab = clear_content(content)
        return content_lab
