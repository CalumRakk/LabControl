import time
import logging

logger = logging.getLogger(__name__)
get_remaining_session_time = (
    lambda t: f"Tiempo restante de la sesión: {t} minutos (~{t/60} horas)"
)


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
