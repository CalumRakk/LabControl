import logging
import time
import requests
from .constants import *
import re

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
        cookies=COOKIES,
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
        cookies=COOKIES,
        headers=HEADERS,
    )

    logger.info(f"status_code: {response.status_code}")
    try:
        return int(r_getMinutes.search(response.text).group())

    except AttributeError as e:
        logger.info(f"response: {response.text}")
        raise e
