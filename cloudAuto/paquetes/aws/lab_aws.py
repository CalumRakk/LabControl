import logging
import json
from typing import Union
from pathlib import Path

from lxml import etree
import vcr
from requests import Response
import requests

from cloudAuto import log_decorator, Config
from . import lab_aws_utils as utils
from .lab_aws_utils import login_decorator
from .constants import LAB_NOT_STARTED, AWSAction, LabStatus, VOCAREUM_VCPU_URL, HEADERS

logger = logging.getLogger(__name__)


class LabAWS:

    def _make_request(self, action: AWSAction) -> Union[Response, dict]:
        """
        Realiza una solicitud a la api de Vocareum utilizando los datos y cookies almacenados.

        Args:
            action (AWSAction): La acción específica que se desea realizar. Este valor se usa para generar los parámetros
                                de la solicitud.

        Returns:
            Union[Response, dict]: Devuelve un objeto `Response` si la solicitud se realiza con éxito. Si los
                                archivos necesarios (cookies y datos) no se encuentran, devuelve un diccionario
                                con la clave "data" establecida en `None` y un mensaje de error bajo la clave
                                "error".
        Raises:
            Exception: Puede lanzar excepciones relacionadas con la lectura de archivos.
        """

        config = Config()
        path_data = Path(config["filepath"]["data_vocareum"])
        path_cookies = Path(config["filepath"]["cookies_vocareum"])
        if not path_cookies.exists() or not path_data.exists():
            return {"data": None, "error": "Files not found"}

        data_vocareum = json.loads(path_data.read_text())
        cookies_vocareum = utils.filter_cookies_for_request(path_cookies)

        response = requests.get(
            url=VOCAREUM_VCPU_URL,
            cookies=cookies_vocareum,
            params=utils.generate_aws_params(action, data_vocareum),
            headers=HEADERS,
        )
        return response

    def _parsing_data(self, data: dict) -> dict:
        # Data es un JSON extraido de una respuesta http devuelto con la accion endaws y startaws
        values = {}
        for text in data["msg"].split("<br>"):
            if text == "":
                continue
            if ":" in text:
                key, value = text.split(":", 1)
                values[key.strip()] = value.strip()
            else:
                values["unparsed_content"] = text + "\n"
        values.update({"status": data["status"]})
        return values

    @login_decorator
    def getaws(self) -> dict:
        """
        Realiza una solicitud para obtener el estado actual del laboratorio en Vocareum y procesa la respuesta.

        Returns:
            dict: Un diccionario que contiene los siguientes elementos:
                - "data": Un sub-diccionario con:
                    - "status": El estado del laboratorio (iniciado, detenido, etc.).
                    - "sessions": Los tiempos de sesión extraídos del contenido HTML.
                    - "expiretime": El tiempo de expiración de la sesión.
                - "error": `None` si la solicitud y el procesamiento fueron exitosos, o un mensaje de error si ocurrió un problema.
        """
        response_status = self.getawsstatus()
        status = response_status["data"]["status"]

        response = self._make_request(AWSAction.getaws)
        root = etree.fromstring(response.text, etree.HTMLParser())

        msg_error = utils.parse_error(root)
        if msg_error:
            return {"data": None, "error": msg_error}

        if status == LabStatus.stopped:
            # font solo está disponible cuando el labotorio está detenido.
            status = getattr(LabStatus, root.find(".//font").text)
        sessiones = utils.extract_session_times(root, status)
        expiretime = utils.get_expire_time(root)
        return {
            "data": {
                "status": status,
                "sessions": sessiones,
                "expiretime": expiretime,
            },
            "error": None,
        }

    @login_decorator
    def startaws(self):
        """
        Envía una solicitud a la API para iniciar o reiniciar el laboratorio.

        La solicitud inicia el laboratorio o reiniciar el tiempo de sesión si el laboratorio ya está iniciado.

        Returns:
            dict: Un diccionario que contiene los siguientes elementos:
                - "data": Los datos procesados extraídos de la respuesta JSON si la solicitud fue exitosa.
                - "error": `None` si la solicitud y el procesamiento fueron exitosos, o un mensaje de error si ocurre algun problema
        """
        # Envia a la api la accion de startaws esto inicia el laboratorio o reinicia el tiempo de session en caso que el laboratorio ya este iniciado.
        # La función endaws siempre devuelve un JSON, independientemente del estado del laboratorio.
        response = self._make_request(AWSAction.startaws)
        try:
            data = json.loads(response.text)
        except ValueError:
            root = etree.fromstring(response.text, etree.HTMLParser())

            msg_error = utils.parse_error(root)
            if msg_error:
                return {"data": None, "error": msg_error}
            else:
                return {"data": None, "error": "Error parsing JSON response"}

        data = json.loads(response.text)
        values = self._parsing_data(data)
        return {"data": values, "error": None}

    @login_decorator
    def getawsstatus(self) -> dict:
        """
        Obtiene el estado actual del laboratorio desde la API.

        Returns:
            dict: Un diccionario que contiene los siguientes elementos:
                - "data": Un sub-diccionario con:
                    - "status": El estado del laboratorio extraído de la respuesta.
                - "error": `None` si la solicitud y el procesamiento fueron exitosos, o un mensaje de error si ocurrió un problema al analizar la respuesta.
        """

        response = self._make_request(AWSAction.getawsstatus)
        root = etree.fromstring(response.text, etree.HTMLParser())

        msg = utils.parse_error(root)
        if msg:
            return {"data": None, "error": msg}

        match = utils.regex_lab_status.search(response.text).group()
        status = getattr(LabStatus, match)
        return {"data": {"status": status}, "error": None}

    @login_decorator
    def endaws(self, force_request=False):
        """
        Envía una solicitud para detener el laboratorio si está en ejecución.

        Si `force_request` es `True`, la solicitud para detener el laboratorio se envía sin importar el estado actual.

        Args:
            force_request (bool): Si es `True`, envia la solicitud para detener el laboratorio independientemente de su estado actual. Si es `False`, solo envía la solicitud para detener el laboratorio si está en ejecución.

        Returns:
            dict: Un diccionario que contiene:
                - "data": Los datos procesados extraídos de la respuesta JSON si la solicitud fue exitosa.
                - "error": `None` si la solicitud y el procesamiento fueron exitosos, o un mensaje de error en caso de problemas al analizar la respuesta JSON o al extraer los datos.
        """
        # Envia a la api la accion de stopped al laboratorio solo si está iniciado.
        # Si se desea forzar la acccion de stoppeal sin importar el estado del laboratorio, se debe establacer force_request=True
        # La función endaws siempre devuelve un JSON, independientemente del estado del laboratorio.

        response_status = self.getawsstatus()
        if force_request is False and response["data"]["status"] == LabStatus.stopped:
            return response_status
        else:
            status = response_status["data"]["status"]

        response = self._make_request(AWSAction.endaws)
        try:
            data = json.loads(response.text)
        except ValueError:
            root = etree.fromstring(response.text, etree.HTMLParser())

            msg_error = utils.parse_error(root)
            if msg_error:
                return {"data": None, "error": msg_error}
            else:
                return {"data": None, "error": "Error parsing JSON response"}

        values = self._parsing_data(data)
        return {"data": {"response": values, "status": status}, "error": None}
