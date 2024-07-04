from .constants import *

from cloudAuto.paquetes.utils import StatusInstance, ActionsInstance
from playwright.sync_api import sync_playwright, expect, Page


def get_test(requests_):
    for request in requests_[1:]:
        for headers in request["headers"]:
            if headers["name"] in REQUIRED_COOKIE_FOR_DescribeInstances:
                print(headers["name"], headers["value"])


def get_url(responses):
    machts = []
    for response in responses:
        if "https://ec2.us-west-2.amazonaws" in response.url:
            machts.append(response)
    return machts


def filter_cookies_browser(cookies_browser: list[dict], contants) -> dict:
    """
    Filtra las cookies del navegador para obtener solo las cookies requeridas.

    Args:
        cookies_browser (list[dict]): Una lista de cookies del navegador.

    Returns:
        dict: Un diccionario que contiene solo las cookies requeridas.
    """
    cookies = {}
    required_cookie_keys = contants.copy()
    for required_key in contants:
        for cookie in cookies_browser:
            if cookie["name"] == required_key:
                cookies.update({required_key: cookie["value"]})
                required_cookie_keys.remove(required_key)
    if len(required_cookie_keys) > 1:
        msg = f"No se encontro en las cookies del navegador las siguienres cookies requeridas: {required_cookie_keys}"
        raise Exception(msg)
    return cookies


def get_language(page: Page) -> str:
    return page.evaluate("() => {return document.documentElement.lang;}")


def get_current_status(page: Page) -> StatusInstance:
    frame = page.frame_locator("#compute-react-frame")
    locator = frame.locator(
        "xpath=//span[span/span[@class='awsui_icon_1cbgc_eofsr_103']]"
    ).first
    language = get_language(page)
    text_status = locator.text_content()
    current_status = translate_status_instance(
        language=language, text_status=text_status
    )
    return current_status


def reload_page(page: Page):
    frame = page.frame_locator("#compute-react-frame")
    button_reload = frame.locator("xpath=//button[@data-testid='action_4']")
    button_reload.wait_for()
    button_reload.click()


def stop_instancia(page: Page):
    current_status = get_current_status(page)
    if current_status.Running:
        locate_instance = frame.locator(
            f"xpath=//tr[//a/text() = '{INSTANCE_ID}']/td[1]/label"
        )
        if locate_instance.is_checked() is False:
            locate_instance.click()

        # Abre el menu de acciones de la instancia
        frame = page.frame_locator("#compute-react-frame")
        frame.locator(
            f"xpath=//div[@class='awsui_dropdown-trigger_sne0l_lqyym_193']/button"
        ).first.click()

        # Hace clic en el botón de apagar
        xpath_actionsInstances = f"xpath=//div[@class='awsui_dropdown-content-wrapper_qwoo0_1jakz_99']//li[@data-testid='{ActionsInstance.Stop.item}']"
        frame.locator(xpath_actionsInstances).click()

        # confirmar el apagado.
        frame.locator(
            "xpath=//button[@data-id='confirmation-modal-primary-btn']"
        ).click()
        return True
    return False


def start_instancia(page: Page):
    current_status = get_current_status(page)
    if current_status.Stopped:
        # Encuentra la fila correspondiente a la instancia
        locate_instance = frame.locator(
            f"xpath=//tr[//a/text() = '{INSTANCE_ID}']/td[1]/label"
        )
        # Si la fila no está seleccionada, la selecciona
        if locate_instance.is_checked() is False:
            locate_instance.click()

        # Abre el menu de acciones de la instancia
        frame = page.frame_locator("#compute-react-frame")
        frame.locator(
            f"xpath=//div[@class='awsui_dropdown-trigger_sne0l_lqyym_193']/button"
        ).first.click()

        # Hace clic en el botón de apagar
        xpath_actionsInstances = f"xpath=//div[@class='awsui_dropdown-content-wrapper_qwoo0_1jakz_99']//li[@data-testid='{ActionsInstance.Start.item}']"
        frame.locator(xpath_actionsInstances).click()
        return True
    return False
