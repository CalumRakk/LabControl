from datetime import timedelta
import re
from lxml import html
def _remove_last_digit(result: list[str]):
    # Elimina el ultimo elemento digito de la segunda posicion de la lista
    result[1] = result[1][:-1]
    return result


def clear_content(content:str):
    root= html.fromstring(content.replace("<br>",""))
    text_content= root.text_content()
    lab_stopped="     Close\t\t \t\t \t\t\xa0\xa0\xa0Cloud Labs\xa0\xa0\xa0"
    if lab_stopped in text_content:
        text_content_clean= text_content.replace(lab_stopped, "")
        result= text_content_clean.split("\xa0\xa0\xa0") 
        return _remove_last_digit(result)
    raise Exception("No se pudo limpiar el contenido")

def parse_accumulated_time(s: str) -> timedelta:
    """
    Parsea un string como:
      "Accumulated lab time: 3 days 06:00:00 (4680 minutes)"
    o
      "Accumulated lab time: 04:59:00 (299 minutes)"
    y devuelve un timedelta.
    """
    # Buscar patrón con días opcionales
    pattern = r"(?:(\d+)\s+days?\s+)?(\d{1,2}):(\d{2}):(\d{2})"
    match = re.search(pattern, s)
    
    if not match:
        raise ValueError(f"No se encontró una duración válida en: {s}")
    
    days = int(match.group(1)) if match.group(1) else 0
    hours = int(match.group(2))
    minutes = int(match.group(3))
    seconds = int(match.group(4))
    
    return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
