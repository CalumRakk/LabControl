from labcontrol.config import Config as LabConfig
from labcontrol.lab_aws_browser import LabAWSBrowserAPI
from labcontrol.lab_aws_http import LabAWSHttpApi
from labcontrol.parser import (
    load_netscape_cookies,
    load_vocareum_params,
    save_netscape_cookies,
)
from labcontrol.schema import VocareumParams


def get_cookies_with_config(config: LabConfig):
    api_http = LabAWSHttpApi([])
    login = api_http.login(config.unique_id, config.password)
    if login.success is False:
        raise Exception(login.error)
    return login.cookies


def get_params_with_config(config: LabConfig) -> VocareumParams:
    """Obtiene los parámetros de Vocareum, usando cookies y login si es necesario."""

    # 1. Si ya tenemos los parámetros guardados, simplemente los cargamos
    if config.vocareum_cookies_path.exists():
        return load_vocareum_params(config.vocareum_cookies_path)

    # 2. Obtener cookies del laboratorio
    if config.lab_cookies_path.exists():
        cookies = load_netscape_cookies(config.lab_cookies_path)
    else:
        cookies = get_cookies_with_config(config)
        save_netscape_cookies(cookies, config.lab_cookies_path)

    # 3. Crear API HTTP y loguearse si hace falta
    api_http = LabAWSHttpApi(cookies)
    if not api_http.is_login():
        login = api_http.login(config.unique_id, config.password)
        if not login.success:
            raise Exception(login.error)
        cookies = login.cookies

    # 4. Obtener parámetros de Vocareum desde el navegador
    api_browser = LabAWSBrowserAPI(cookies, headless=True)
    try:
        params = api_browser.get_vocareum_params()
        config.vocareum_cookies_path.write_text(params.model_dump_json())
    finally:
        api_browser.browser.stop()

    return params
