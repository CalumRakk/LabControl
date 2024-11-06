#
# Script para que el laboratorio siga activo por más de 4 horas
#

from labcontrol import LabAWS
from labcontrol.constants import LabStatus
import random
import logging
import utils
import time

logger = logging.getLogger(__name__)


class LabController:
    def __init__(self):
        self.lab = LabAWS()

    def wait_for_lab_to_start(self):
        logger.info("Esperando al laboratorio a iniciar")
        while self.lab.status != LabStatus.ready:
            time.sleep(1)

    def get_data_from_lab(self):
        data = self.lab.getaws()
        if data["data"]["status"] != LabStatus.ready:
            self.lab.start()
            self.wait_for_lab_to_start()
            data = self.lab.getaws()
        return data

    def get_remaining_session_time(self, data):
        remaining_time_str = data["data"]["sessions"]["remaining_time"]
        return int(remaining_time_str.split("(")[-1].split()[0])

    def maintain_session_time(self):
        logger.info("El programa se ha iniciado")
        data = self.get_data_from_lab()
        min_remaining = self.get_remaining_session_time(data)
        logger.info(utils.get_remaining_session_time(min_remaining))

        if min_remaining > 120:
            difference_in_sec = (min_remaining - 120) * 60
            utils.sleep_program(difference_in_sec)

        while True:
            random_wait_minutes = random.randint(5, 15)
            logger.info(f"Tiempo random de espera {random_wait_minutes} minutos")
            utils.sleep_program(random_wait_minutes * 60)

            data = self.get_data_from_lab()
            min_remaining = self.get_remaining_session_time(data)
            logger.info(utils.get_remaining_session_time(min_remaining))
            difference_in_sec = (min_remaining - 120) * 60
            utils.sleep_program(difference_in_sec)


if __name__ == "__main__":
    controller = LabController()
    controller.maintain_session_time()
