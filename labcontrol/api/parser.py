from http.cookiejar import Cookie
from urllib.parse import unquote
from typing import List, Dict, Union

from labcontrol.api.browser.driver import Path

SeleniumCookie = Dict[str, Union[str, bool]]

def cookies_to_requests(raw: str) -> Dict[str, str]:
    """
    Convierte un header Cookie o Set-Cookie en un dict simple para requests.
    """
    cookies = {}
    # Dividir por coma solo cuando empieza una nueva cookie (key=...)
    parts = [p.strip() for p in raw.split(",")]
    for part in parts:
        segments = [s.strip() for s in part.split(";")]
        if "=" in segments[0]:
            name, value = segments[0].split("=", 1)
            cookies[name] = unquote(value)  # decodifica %xx
    return cookies


def cookies_to_selenium(raw: str, domain: str) -> List[Dict]:
    """
    Convierte un header Cookie o Set-Cookie en el formato esperado por Selenium.
    """
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