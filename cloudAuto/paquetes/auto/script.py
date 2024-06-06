import logging
from .utils import sleep_program, get_getaws, get_startaws
import random
from ..utils.constants.status import SingletonMeta
from cloudAuto.paquetes.utils import ActionsInstance, StatusInstance


class Auto(metaclass=SingletonMeta):
    def __init__(self):
        self.status = StatusInstance.Stopped

    def start(self):
        self.status = StatusInstance.Pending
        logger = logging.getLogger(__name__)
        logger.info("El programa se ha iniciado")

        remaining_session_time = (
            lambda t: f"Tiempo restante de la sesión: {t} minutos (~{t/60} horas)"
        )

        min_remaining = get_getaws()
        logger.info(remaining_session_time(min_remaining))

        # Si a la session le quedan más de dos horas, saca la diferencia y espera a que llegue a dos horas.
        if min_remaining > 120:
            difference_in_seg = (min_remaining - 120) * 60

            sleep_program(difference_in_seg)

        min_remaining = get_startaws()
        logger.info(remaining_session_time(min_remaining))
        difference_in_seg = (min_remaining - 120) * 60
        sleep_program(difference_in_seg)

        while True:
            random_wait_minutes = random.randint(5, 15)
            logger.info(f"Tiempo random de espera {random_wait_minutes} minutos")
            sleep_program(random_wait_minutes * 60)

            min_remaining = get_startaws()
            logger.info(remaining_session_time(min_remaining))
            difference_in_seg = (min_remaining - 120) * 60
            sleep_program(difference_in_seg)
