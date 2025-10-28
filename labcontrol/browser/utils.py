import re
from datetime import timedelta

from lxml import html


def _remove_last_digit(result: list[str]):
    # Elimina el ultimo elemento digito de la segunda posicion de la lista
    result[1] = result[1][:-1]
    return result


def clear_content(content: str):
    root = html.fromstring(content.replace("<br>", ""))
    text_content = root.text_content()

    if "stopped" in text_content:
        text_content_clean = text_content.split("\xa0\xa0\xa0")[2:]
        return _remove_last_digit(text_content_clean)

    elif "AWS CLI" in text_content:
        text_content_clean = text_content.split("\xa0\xa0\xa0")[2:7]
        # ignora las lineas:
        # - 'No running instance'
        # - 'SSH key\xa0\xa0ShowDownload PEMDownload PPK'
        # - 'AWS SSO\xa0\xa0Download URL-----BEGIN RSA PRIVATE KEY-----...'

        elements = root.xpath(".//button[contains(@onclick, 'ssodownload')]")
        if elements:
            attr_onclikk = elements[0].get("onclick", "")
            sso_download_part = re.search(r"ssodownload\('([^']+)'\)", attr_onclikk)
            if sso_download_part:
                sso_download_url = sso_download_part.group(1)
                text_content_clean.append(f"AWS SSO\xa0\xa0{sso_download_url}")
        return text_content_clean

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
