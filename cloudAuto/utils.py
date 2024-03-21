import logging
import time
import re
import random
import json
from datetime import datetime
from .constants import *
from typing import Union
import requests
from playwright.sync_api import sync_playwright
from playwright._impl._errors import TimeoutError
from lxml import etree


delay = lambda: random.uniform(200, 500)
get_currentUrl = lambda page: page.evaluate("() => {return window.location.href;}")


logging.basicConfig(
    filename="log.txt",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%m-%Y %I:%M:%S %p",
    level=logging.INFO,
    encoding="utf-8",
)
logger = logging.getLogger(__name__)

r_getMinutes = re.compile(r"(?<=\()\d+(?= \w+\))")
r_getCookies = re.compile(r"(?<=cookie:\s).*?(?=')")

file_cookies_last_modified = None
current_cookies = None


def seconds_to_timeh(seconds):
    horas = seconds // 3600
    minutos = (seconds % 3600) // 60
    segundos = (seconds % 3600) % 60

    horasString = str(horas).zfill(2)
    minutosString = str(minutos).zfill(2)
    segundosString = str(segundos).zfill(2)

    return f"{horasString}:{minutosString}:{segundosString}"


def sleep_program(sleep_seconds: int):
    if sleep_seconds > 0:
        logger.info(
            f"El programa entro en modo sueño: {seconds_to_timeh(sleep_seconds)}"
        )

    while sleep_seconds > 0:
        print(f"Tiempo restante: {seconds_to_timeh(sleep_seconds)}", end="\r")

        sleep_seconds -= 1
        time.sleep(1)


def load_cookies_browser() -> list[dict]:
    """
    Carga las cookies del archivo de cookies del navegador si está disponible.

    Returns:
        list[dict]: Una lista de cookies del navegador cargadas desde el archivo.
    """
    if PATH_COOKIES_BROWSER.exists():
        try:
            content = PATH_COOKIES_BROWSER.read_text()
            cookies = json.loads(content)
            logger.info(
                f"Se han cargado las cookies del archivo {PATH_COOKIES_BROWSER.name}."
            )
            return cookies
        except TypeError as e:
            logger.warning(
                f"No se pudo deserializar las cookies del archivo {PATH_COOKIES_BROWSER.name}."
            )
            raise e
    else:
        msg = f"No se encontró el archivo {PATH_COOKIES_BROWSER.name} para cargar las cookies."
        logger.warning(msg)
        return Exception(msg)


def cookies_expired(cookies: Union[dict, list[dict]]):
    """
    Verifica si las cookies han expirado.

    La función admite cookies del navegador o un diccionario de cookies.

    Args:
        cookies (Union[dict, list[dict]]): Las cookies a verificar.

    Returns:
        bool: True si las cookies han expirado, False en caso contrario.
    """

    def get_tokenExpire() -> int:
        if isinstance(cookies, list):
            for cookie in cookies:
                if cookie["name"] == "tokenExpire":
                    return int(cookie["value"])
        elif isinstance(cookies, dict):
            return int(cookies["tokenExpire"])
        error = "Cookies debe que ser un diccionario o lista de diccionario"
        logger.error(error)
        raise Exception(error)

    tokenExpire = get_tokenExpire()
    date = datetime.fromtimestamp(tokenExpire)
    date_string = date.strftime("%d-%m-%Y %I:%M:%S %p")
    if datetime.now() >= date:
        logger.error(
            f"Las cookies de 'Cookies Browser' han expirado. Fecha de expiración: {date_string}"
        )
        return True
    logger.info(
        f"Las cookies de 'Cookies Browser' no han expirado. Fecha de expiración: {date_string}"
    )
    return False


def filter_cookies_browser(cookies_browser: list[dict]) -> dict:
    """
    Filtra las cookies del navegador para obtener solo las cookies requeridas.

    Args:
        cookies_browser (list[dict]): Una lista de cookies del navegador.

    Returns:
        dict: Un diccionario que contiene solo las cookies requeridas.
    """
    cookies = {}
    required_cookie_keys = REQUIRED_COOKIE_KEYS.copy()
    for required_key in REQUIRED_COOKIE_KEYS:
        for cookie in cookies_browser:
            if cookie["name"] == required_key:
                cookies.update({required_key: cookie["value"]})
                required_cookie_keys.remove(required_key)
    if len(required_cookie_keys) > 1:
        msg = f"No se encontro en las cookies del navegador las siguienres cookies requeridas: {required_cookie_keys}"
        logger.error(msg)
        raise Exception(msg)
    return cookies


def get_user() -> tuple[str, str]:
    if PATH_USER.exists():
        username, password = PATH_USER.read_text().split(":")
    else:
        username = input("Username>>>")
        password = input("Password>>>")
    return username.strip(), password.strip()


def login(func):
    """
    Decorador que maneja el inicio de sesión y las cookies.

    El decorador carga las cookies del navegador si están disponibles y válidas.
    Si las cookies han expirado o no están disponibles, inicia sesión nuevamente y actualiza las cookies.

    Args:
        func (callable): La función que se va a decorar.

    Returns:
        callable: La función decorada.
    """

    def wrapper():
        try:
            return func()
        except AttributeError:
            logger.info(f"Fallo la solicitud")
            try:
                cookies_browser = load_cookies_browser()
                cookies = filter_cookies_browser(cookies_browser)
                if cookies_expired(cookies) is False:
                    PATH_COOKIES.write_text(json.dumps(cookies))
                    logger.info(
                        f"Se guardo el diccionario de cookies en el archivo {PATH_COOKIES.name}"
                    )
                    return func()
            except (TypeError, Exception):
                pass

            username, password = get_user()
            cookies_browser = login_and_get_cookies(
                username=username, password=password
            )
            PATH_COOKIES_BROWSER.write_text(json.dumps(cookies_browser))
            cookies = filter_cookies_browser(cookies_browser)
            PATH_COOKIES.write_text(json.dumps(cookies))
            logger.info(f"Se guardo el diccionario de cookies y cookies del navegador")
            return func()

    return wrapper


@login
def get_getaws() -> int:
    cookies = load_cookies()

    logger.info(
        f"solicitud a la URL {URL_GETAWS} con la carga útil de la constante PARAMS_GETAWS"
    )

    response = requests.get(
        URL_GETAWS,
        params=PARAMS_GETAWS,
        cookies=cookies,
        headers=HEADERS,
    )

    logger.info(f"status_code: {response.status_code}")
    try:
        parser = etree.HTMLParser()
        root = etree.fromstring(response.text, parser)
        expiretime = root.find(".//span[@id='vlab-expiretime']").text
        expitedate = datetime.fromtimestamp(int(expiretime))
        seconds = (expitedate - datetime.now()).seconds

        if seconds > 0:
            return int(seconds) // 60
        return 0
    except AttributeError as e:
        logger.info(f"response: {response.text}")
        raise e


@login
def get_startaws() -> int:
    cookies = load_cookies()
    logger.info(
        f"solicitud a la URL {URL_GETAWS} con la carga útil de la constante PARAMS_STARTAWS"
    )

    response = requests.get(
        URL_GETAWS,
        params=PARAMS_STARTAWS,
        cookies=cookies,
        headers=HEADERS,
    )

    logger.info(f"status_code: {response.status_code}")
    try:
        return int(r_getMinutes.search(response.text).group())
    except AttributeError as e:
        logger.info(f"response: {response.text}")
        raise e


def load_cookies() -> dict:
    """
    Carga las cookies desde un archivo si están disponibles y si ha habido modificaciones recientes en el archivo.

    Returns:
        dict: Un diccionario que contiene las cookies cargadas desde el archivo.
    """
    global file_cookies_last_modified
    global current_cookies

    if PATH_COOKIES.exists():
        mtime = PATH_COOKIES.stat().st_mtime
        current_file_cookies_last_modified = datetime.fromtimestamp(mtime)
        try:
            if current_file_cookies_last_modified != file_cookies_last_modified:
                content = PATH_COOKIES.read_text()
                current_cookies = json.loads(content)
                if file_cookies_last_modified:
                    msg = f"Se encontraron modificaciones en el archivo de cookies: {PATH_COOKIES.name}."
                    logger.info(msg)
                file_cookies_last_modified = current_file_cookies_last_modified
                return current_cookies

            content = PATH_COOKIES.read_text()
            current_cookies = json.loads(content)
            logger.info(f"Se han cargado las cookies del archivo {PATH_COOKIES.name}.")
            return current_cookies
        except TypeError as e:
            msg = f"No se pudo deserializar las cookies del archivo {PATH_COOKIES.name}"
            logger.warning(msg)
    else:
        msg = f"No se encontró el archivo {PATH_COOKIES.name} para cargar las cookies."
        logger.warning(msg)
    return {}


def parse_curl_to_json(cUrl) -> dict:
    """De un comando cUrl extrae las cookies en formato json"""
    match = r_getCookies.search(cUrl)
    if match:
        cookies_string = r_getCookies.search(cUrl).group()
        keys_string = cookies_string.split(";")
        cookies = {}
        for key_string in keys_string:
            key, value = key_string.split("=")
            cookies.update({key: value})
        return cookies


def login_and_get_cookies(username, password, headless=True) -> list[dict]:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        )
        page = context.new_page()
        logger.info("Navegador web cargado.")

        page.goto(URL_LOGIN)
        logger.info(f"Se cargó la siguiente URL: {get_currentUrl(page)}")

        logger.info("Tipeando las credenciales en el formulario de login de la página.")
        page.keyboard.type(username, delay=delay())
        page.keyboard.press("Tab")
        page.keyboard.type(password, delay=delay())
        page.query_selector("[type='submit']").click()
        logger.info("Se envió el formulario de inicio de sesión.")

        # Una pequeña espera antes de visitar la URL de la carga de laboratorio.
        logger.info("Esperando antes de visitar la URL de carga de laboratorio.")
        sleep_program(random.randint(1, 10))
        page.goto(URL_LAB)
        status = page.evaluate("() => {return document.readyState;}")
        logger.info(
            f"Se cargó la siguiente URL: {get_currentUrl(page)} con status: {status}"
        )
        sleep_program(random.randint(1, 10))
        page.query_selector("[type='submit']").click()
        logger.info("Haciendo clic en el botón 'Cargar Laboratorio'.")

        logger.info("Esperando a que haya dos pestañas antes de continuar...")
        seg = 0
        while len(context.pages) < 2:
            seg += 1
            time.sleep(1)
            if seg >= 15:
                logger.info("Haciendo clic en el botón 'Cargar Laboratorio'.")
                try:
                    element = page.query_selector("[type='submit']")
                    element.click()
                except TimeoutError:
                    logger.error(
                        "Error TimeoutError al hacer clic en el botón 'Cargar Laboratorio'."
                    )
                seg = 0

        logger.info(
            "Esperando a que se complete la carga de la página de la nueva pestaña."
        )
        NewPageReturned = context.pages[1]
        while True:
            status = NewPageReturned.evaluate("() => {return document.readyState;}")
            if status == "complete":
                break
            time.sleep(1)
        logger.info("Se completó la carga del laboratorio.")

        cookies = context.cookies()
        logger.info("Devolviendo las cookies del navegador.")
        return cookies
