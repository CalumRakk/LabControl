from datetime import datetime
from urllib.parse import unquote
from typing import List, Dict, Union
from pathlib import Path

from labcontrol.browser.utils import parse_accumulated_time

SeleniumCookie = Dict[str, Union[str, bool]]

def cookies_to_requests(raw: str) -> Dict[str, str]:
    """
    Convierte un header Cookie o Set-Cookie en un dict simple para requests. Esto implica unquote de los valores.
    """
    # TODO: agregar set_cookie en el nombre
    cookies = {}
    # Dividir por coma solo cuando empieza una nueva cookie (key=...)
    parts = [p.strip() for p in raw.split(",")]
    for part in parts:
        segments = [s.strip() for s in part.split(";")]
        if "=" in segments[0]:
            name, value = segments[0].split("=", 1)
            cookies[name] = unquote(value)  # decodifica %xx
    return cookies


def cookies_to_selenium(raw: str, domain: str) -> List[SeleniumCookie]:
    """
    Convierte un header Cookie o Set-Cookie en el formato esperado por Selenium.
    """
    # TODO: agregar set_cookie en el nombre o un mejor indicador
    selenium_cookies = []
    parts = [p.strip() for p in raw.split(",")]
    for part in parts:
        segments = [s.strip() for s in part.split(";")]
        if "=" not in segments[0]:
            continue
        name, value = segments[0].split("=", 1)
        cookie_dict : SeleniumCookie = {
            "name": name,
            "value": unquote(value),
            "domain": domain,
            "path": "/"
        }
        # Procesar atributos como path, secure, httponly
        for attr in segments[1:]:
            if "=" in attr:
                k, v = attr.split("=", 1)
                if k.lower() == "path":
                    cookie_dict["path"] = v
            else:
                # Flags sin valor: secure, httponly, etc.
                if attr.lower() == "secure":
                    cookie_dict["secure"] = True
                if attr.lower() == "httponly":
                    cookie_dict["httpOnly"] = True

        selenium_cookies.append(cookie_dict)
    return selenium_cookies

def load_netscape_cookies(filepath: Union[str, Path]) -> List[SeleniumCookie]:
    filepath = Path(filepath) if isinstance(filepath, str) else filepath
    cookies = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue  # ignorar comentarios y líneas vacías

            domain, flag, path, secure, expiration, name, value = line.split("\t")

            cookie = {
                "domain": domain,
                "path": path,
                "secure": secure.lower() == "true",
                "expiry": int(expiration),
                "name": name,
                "value": value,
            }
            cookies.append(cookie)
    return cookies

def parse_lab_aws_details_content(content_lab:list[str])->dict:
    data={}
    if len(content_lab)==3:
        # el laboratorio no ha iniciado.
        session_time_string = content_lab[0]
        session_status_time = content_lab[1]
        accumulated_lab_time = content_lab[2]
    
        # --- parse session_time_string ---
        session_time_value= session_time_string.split(":",1)[-1].strip()         
        if session_time_value.startswith("-"):
            data["session_started_at"] = None
        else:              
            data["session_started_at"] = datetime.strptime(session_time_value, "%Y-%m-%dT%H:%M:%S%z")
    
        # --- parse session_status_time ---
        status= session_status_time.split()[1].strip()
        status_time= session_status_time.split()[-1].strip()
       
        data["session_status"] = status
        data["session_status_time"] =  datetime.strptime(status_time, "%Y-%m-%dT%H:%M:%S%z")

        # --- parse accumulated_lab_time ---

        data["accumulated_lab_time"] = parse_accumulated_time(accumulated_lab_time)
        return data
    raise ValueError