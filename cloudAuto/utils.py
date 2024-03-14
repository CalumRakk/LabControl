import logging
import time
import requests
import re
from datetime import datetime
from .constants import *


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

curl_txt_last_modified = None
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


def get_getaws() -> int:
    logger.info(
        f"solicitud a la URL {URL_GETAWS} con la carga útil de la constante PARAMS_GETAWS"
    )

    response = requests.get(
        URL_GETAWS,
        params=PARAMS_GETAWS,
        cookies=load_cookies(),
        headers=HEADERS,
    )

    logger.info(f"status_code: {response.status_code}")
    try:
        return int(r_getMinutes.search(response.text).group())

    except AttributeError as e:
        logger.info(f"response: {response.text}")
        raise e


def get_startaws() -> int:
    logger.info(
        f"solicitud a la URL {URL_GETAWS} con la carga útil de la constante PARAMS_STARTAWS"
    )

    response = requests.get(
        URL_GETAWS,
        params=PARAMS_STARTAWS,
        cookies=load_cookies(),
        headers=HEADERS,
    )

    logger.info(f"status_code: {response.status_code}")
    try:
        return int(r_getMinutes.search(response.text).group())

    except AttributeError as e:
        logger.info(f"response: {response.text}")
        raise e


def load_cookies() -> dict:
    global curl_txt_last_modified
    global current_cookies

    path = Path("cUrl.txt")
    stat = path.stat().st_mtime
    current_last_modified = datetime.fromtimestamp(stat)

    if current_last_modified != curl_txt_last_modified:
        cUrl = path.read_text()
        current_cookies = parse_curl_to_json(cUrl)
        curl_txt_last_modified = current_last_modified
        logger.info("Las Cookies se han cargado.")
    return current_cookies


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
