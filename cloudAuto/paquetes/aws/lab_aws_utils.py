import json
import re
from enum import Enum
from datetime import datetime
from typing import Union
from pathlib import Path

import requests

from cloudAuto import Config
from .constants import LabStatus, LAB_NOT_STARTED, LOGIN_AGAIN_MESSAGE
from .browser import Browser
from .constants import AWSAction


HEADERS = {
    "accept": "*/*",
    "accept-language": "es-419,es;q=0.9",
    "priority": "u=1, i",
    "sec-ch-ua": '"Not;A=Brand";v="24", "Chromium";v="128"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}


VOCAREUM_VCPU_URL = "https://labs.vocareum.com/util/vcput.php"


COOKIE_KEYS_FOR_REQUEST = [
    "logintoken",
    "tokenExpire",
    "usertoken",
    "userid",
    "t2fausers",
    "usingLTI",
    "myfolder",
    "currentcourse",
    "currentassignment",
]


def login_decorator(func):
    def wrapper(*args, **kwargs):
        data = func(*args, **kwargs)
        if data["error"] == LOGIN_AGAIN_MESSAGE:
            browser = Browser()
            browser.load_aws()
            return func(*args, **kwargs)

        return data

    return wrapper


REGEX_HOURS = r"\s?\d\d:\d\d:\d\d"  # 00:01:00
REGEX_DATE = r"\d{4}-\d+-\d+T\d+:\d+:\d+-\d{4}"  # 2024-08-20T18:18:55-0700
REGEX_MINUTES_PATTERN = r"\s?(\(\d+\s\w+\))"  # (4680 minutes)
REGEX_HDATE_AND_HOURS = rf"\d+\s\w+\s{REGEX_HOURS}"  # 3 days 06:00:00 (4680 minutes)

regex_lab_status = re.compile("(?<=Lab status: )\w.*(?=<br>)")


class ReadyLabSessionRegex(Enum):
    """Regex para capturar los tiempos de session del Laboratorio cuando está iniciado."""

    remaining_time = re.compile(
        rf"Remaining session time:\s{REGEX_HOURS}{REGEX_MINUTES_PATTERN}"
    )
    session_started = re.compile(f"Session started at:\s{REGEX_DATE}")
    session_ended = re.compile(f"Session to end(.*)?at:\s{REGEX_DATE}")
    accumulated_lab_time = re.compile(
        rf"Accumulated lab time:\s?({REGEX_HOURS}|{REGEX_HDATE_AND_HOURS}){REGEX_MINUTES_PATTERN}"
    )


class StoppedLabSessionRegex(Enum):
    """Regex para capturar los tiempos de session del Laboratorio cuando está detenido."""

    session_started = re.compile(f"Session started at:\s-0001-11-30T00:00:00-0752")
    session_stopped = re.compile(f"Session stopped(.*)?at \s?{REGEX_DATE}")
    accumulated_lab_time = re.compile(
        rf"Accumulated lab time:\s?({REGEX_HOURS}|{REGEX_HDATE_AND_HOURS}){REGEX_MINUTES_PATTERN}"
    )


def extract_session_times(root, status: LabStatus):
    """
    Extrae los tiempos de sesión del contenido HTML basado en el estado del laboratorio.

    Args:
        root: El contenido de la respuesta HTTP parseado lxml
        status (LabStatus): El estado del laboratorio, que puede ser `LabStatus.ready` o `LabStatus.stopped`.

    Returns:
        dict: Un diccionario con los tiempos de sesión extraídos, donde las claves corresponden a los nombres
              de los miembros del enum relacionado con el estado del laboratorio. Devuelve `None` si el estado
              del laboratorio no es 'ready' ni 'stopped'.
    """

    content = "".join([text for text in root.find(".//body").itertext()])

    # Con el status se determina que regex usar para extraer los tiempos de sesión
    if status == LabStatus.ready:
        regex_enum = ReadyLabSessionRegex
    elif status == LabStatus.stopped:
        regex_enum = StoppedLabSessionRegex
    else:
        return None

    dataa = {}
    for key, enum in regex_enum.__members__.items():
        match = enum.value.search(content)
        dataa[key] = match.group()
    return dataa


def extract_status(root) -> LabStatus:
    """Devuelve un estado especifico del laboratorio si en el root encuentra uno de los siguientes casos:
    - Si encuentra un elemento font devuelve LabStatus.stopped
    -
    """
    element = root.find(".//font")
    if element is not None:
        return LabStatus.stopped

    element = root.find(".//span[@id='vlab-expiretime']")
    return LabStatus.ready


def filter_cookies_for_request(cookies_browser: Union[list[dict], Path]) -> dict:
    """
    Filtra las cookies del navegador para que coincidan con las claves requeridas para la solicitud.

    Args:
        cookies_browser (Union[list[dict], Path]): El path o una lista de cookies del navegador, donde cada cookie está representada como un diccionario.

    Returns:
        dict: Un diccionario que contiene solo las cookies requeridas para la solicitud.

    Raises:
        Exception: Si faltan algunas claves requeridas en las cookies del navegador.
    """
    if isinstance(cookies_browser, Path):
        cookies_browser = json.loads(cookies_browser.read_text())

    cookies = {}
    required_cookie_keys = COOKIE_KEYS_FOR_REQUEST.copy()
    for required_key in COOKIE_KEYS_FOR_REQUEST:
        for cookie in cookies_browser:
            if cookie["name"] == required_key:
                cookies.update({required_key: cookie["value"]})
                required_cookie_keys.remove(required_key)
    if len(required_cookie_keys) > 1:
        msg = f"No se encontraron en las cookies del navegador las siguientes cookies requeridas: {required_cookie_keys}"
        raise Exception(msg)
    return cookies


def parse_error(root):
    """
    Devuelve un mensaje de error si encuentra uno de los siguientes casos en el root:
    - Si encuentra el elemento error:invalid_session
    - Si el body del root es igual al texto de la constante LAB_NOT_STARTED
    - Si ninguno de los casos anteriores se cumple, devuelve None
    Args:
        root: El elemento raíz del árbol XML/HTML.
    """
    target = root.find(".//error:invalid_session")
    if target is not None:
        return target.text.strip()  # Please login again

    content = "".join([text for text in root.find(".//body").itertext()])
    if content == LAB_NOT_STARTED:
        return LAB_NOT_STARTED

    return None


# def extract_content(root):
#     return " ".join([text.strip() for text in root.find("body").itertext()])


def get_expire_time(root):
    expiretime = int(root.find(".//span[@id='vlab-expiretime']").text)
    return datetime.fromtimestamp(expiretime)


def get_aws_credentials(root):
    span_aws_cli = root.find(".//div[@id='clikeybox'].//span")
    return re.findall("(\w+=\w+)", span_aws_cli.text)


####


def generate_aws_params(action: AWSAction, data_vocareum: dict):
    return {
        "a": action.value,
        "type": "1",
        "stepid": data_vocareum["stepid"],
        "version": "0",
        "v": "0",
        "vockey": data_vocareum["vockey"],
    }


def load_paths() -> tuple[Path, Path]:
    """
    Devuelve las rutas de los archivos `data_vocareum` y `cookies_vocareum` a partir de Config.

    Returns:
        tuple[Path, Path]: Una tupla que contiene las rutas a los archivos `data_vocareum` y `cookies_vocareum`.
    """

    config = Config()
    path_data_vocareum = Path(config["filepath"]["data_vocareum"])
    path_cookies_vocareum = Path(config["filepath"]["cookies_vocareum"])

    return path_data_vocareum, path_cookies_vocareum


def load_data_and_cookies(path_data_vocareum: Path, path_cookies_vocareum: Path):
    """
    Carga los datos y las cookies desde las rutas especificadas.

    Args:
        path_data_vocareum (Path): Ruta al archivo `data_vocareum`.
        path_cookies_vocareum (Path): Ruta al archivo `cookies_vocareum`.

    Returns:
        tuple: Datos de `data_vocareum` y cookies filtradas de `cookies_vocareum`.
    """

    data_vocareum = json.loads(path_data_vocareum.read_text())
    cookies_vocareum = filter_cookies_for_request(path_cookies_vocareum)
    return data_vocareum, cookies_vocareum


def make_request_to_cloud(action: AWSAction, data_vocareum, cookies_vocareum):
    response = requests.get(
        url=VOCAREUM_VCPU_URL,
        cookies=cookies_vocareum,
        params=generate_aws_params(action, data_vocareum),
        headers=HEADERS,
    )
    return response
