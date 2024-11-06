#
# Script para que el laboratorio siga activo por más de 4 horas
#

from labcontrol import LabAWS
from labcontrol.constants import LabStatus
import random
import logging
import utils
import time


# Esperar a que el laboratorio inicie
def wait_for_lab_to_start(lab: LabAWS):
    logger.info("Esperando al laboratorio a iniciar")
    while True:
        if lab.status != LabStatus.ready:
            time.sleep(1)
        break


def get_data_from_lab(lab: LabAWS):
    data = lab.getaws()

    if data["data"]["status"] != LabStatus.ready:
        lab.start()
        wait_for_lab_to_start(lab)
        data = lab.getaws()

    return data


logger = logging.getLogger(__name__)

logger.info("El programa se ha iniciado")
lab = LabAWS()
data = get_data_from_lab(lab)


min_remaining = int(
    data["data"]["sessions"]["remaining_time"].split("(")[-1].split()[0]
)

logger.info(utils.get_remaining_session_time(min_remaining))

# Si a la session le quedan más de dos horas, saca la diferencia y espera a que llegue a dos horas.
if min_remaining > 120:
    difference_in_seg = (min_remaining - 120) * 60
    utils.sleep_program(difference_in_seg)

data = lab.start()
data = get_data_from_lab(lab)
min_remaining = int(
    data["data"]["sessions"]["remaining_time"].split("(")[-1].split()[0]
)
logger.info(utils.get_remaining_session_time(min_remaining))
difference_in_seg = (min_remaining - 120) * 60
utils.sleep_program(difference_in_seg)

while True:
    random_wait_minutes = random.randint(5, 15)
    logger.info(f"Tiempo random de espera {random_wait_minutes} minutos")
    utils.sleep_program(random_wait_minutes * 60)

    data = lab.start()
    data = get_data_from_lab(lab)
    min_remaining = int(
        data["data"]["sessions"]["remaining_time"].split("(")[-1].split()[0]
    )
    logger.info(utils.get_remaining_session_time(min_remaining))
    difference_in_seg = (min_remaining - 120) * 60
    utils.sleep_program(difference_in_seg)
