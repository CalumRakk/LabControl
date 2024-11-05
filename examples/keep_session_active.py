#
# Script para que el laboratorio siga activo por más de 4 horas
#

from labcontrol import LabAWS
import random
import logging
import utils

logger = logging.getLogger(__name__)

logger.info("El programa se ha iniciado")
lab = LabAWS()
data = lab.getaws()

min_remaining = int(
    data["data"]["sessions"]["remaining_time"].split("(")[-1].split()[0]
)

logger.info(utils.get_remaining_session_time(min_remaining))

# Si a la session le quedan más de dos horas, saca la diferencia y espera a que llegue a dos horas.
if min_remaining > 120:
    difference_in_seg = (min_remaining - 120) * 60
    utils.sleep_program(difference_in_seg)

data = lab.start()
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
    min_remaining = int(
        data["data"]["sessions"]["remaining_time"].split("(")[-1].split()[0]
    )
    logger.info(utils.get_remaining_session_time(min_remaining))
    difference_in_seg = (min_remaining - 120) * 60
    utils.sleep_program(difference_in_seg)
