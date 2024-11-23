#
# Script para que el laboratorio siga activo por más de 4 horas
#

from labcontrol import LabAWS
from labcontrol.lab_aws_utils import download_aws_sso
from labcontrol.constants import LabStatus
import logging
import time
from datetime import timedelta

logger = logging.getLogger(__name__)


class LabController:
    def __init__(self):
        self.lab = LabAWS()

    def wait_for_lab_to_start(self):
        logger.info("Esperando al laboratorio a iniciar")
        while self.lab.status != LabStatus.ready:
            time.sleep(1)

    def get_remaining_session_time(self, data):
        remaining_time_str = data["data"]["sessions"]["remaining_time"]
        minutes = int(remaining_time_str.split("(")[-1].split()[0])
        return timedelta(minutes=minutes)

    def check_status(self):
        """
        Comprueba el estado del laboratorio.
        Si el laboratorio no está en ejecución, inicia el laboratorio y teniene el programa hasta que inicie el laboratorio
        """
        logger.debug(f"Status del laboratorio: {self.lab.status}")
        if self.lab.status != LabStatus.ready:
            logger.debug("Iniciando laboratorio")
            self.lab.start()
            self.wait_for_lab_to_start()
            logger.debug(f"Status del laboratorio: {self.lab.status}")

    def get_min_remaining_time(self):
        data = self.lab.getaws()
        download_aws_sso(data["data"]["aws_sso"])
        min_remaining = self.get_remaining_session_time(data)
        logger.debug(f"Tiempo restante de la sesión obtenido: {min_remaining}")
        return min_remaining

    def waiting(self, min_remaining: timedelta):
        """
        Si min_remaining es mayor a 2 horas, el programa se pausa hasta que min_remaining sea menor a 2 horas
        """
        hours = timedelta(hours=2)
        if min_remaining > hours:
            logger.debug(f"El tiempo de la session supera las {hours} horas")
            difference_in_sec = min_remaining - hours
            self.sleep_program(int(difference_in_sec.total_seconds()))

    def sleep_program(self, sleep_seconds: int):
        if sleep_seconds <= 0:
            return

        logger.info(
            f"El programa entro en modo sueño: {timedelta(seconds=sleep_seconds)}"
        )
        while sleep_seconds > 0:
            print(f"Tiempo restante: {timedelta(seconds=sleep_seconds)}", end="\r")
            sleep_seconds -= 1
            time.sleep(1)

    def maintain_session_time(self):
        logger.info(
            """\n
            =================================
                El programa se ha iniciado
            =================================
            \n"""
        )

        while True:
            self.check_status()
            min_remaining = self.get_min_remaining_time()
            self.waiting(min_remaining)
            logger.debug("Reiniciando el laboratorio")
            self.lab.start()


if __name__ == "__main__":
    controller = LabController()
    controller.maintain_session_time()
