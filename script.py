from labcontrol.config import get_settings
from labcontrol.lab_aws_browser import LabAWSBrowserAPI
from labcontrol.lab_aws_http import LabAWSHttpApi
from labcontrol.parser import (
    load_netscape_cookies,
    load_vocareum_params,
    save_netscape_cookies,
)
from labcontrol.vocareum_http import VocareumApi

config = get_settings(".env/labcontrol.env")


def get_cookies_with_config(config):
    api_http = LabAWSHttpApi([])
    login = api_http.login(config.unique_id, config.password)
    if login.success is False:
        raise Exception(login.error)
    return login.cookies


if not config.vocareum_cookies_path.exists():
    if not config.lab_cookies_path.exists():
        cookies = get_cookies_with_config(config)
        save_netscape_cookies(cookies, config.lab_cookies_path)
    else:
        cookies = load_netscape_cookies(config.lab_cookies_path)

    api_http = LabAWSHttpApi(cookies)
    if not api_http.is_login():
        login = api_http.login(config.unique_id, config.password)
        if login.success is False:
            raise Exception(login.error)
        cookies = login.cookies

    api_browser = LabAWSBrowserAPI(cookies, headless=True)
    params = api_browser.get_vocareum_params()
    model_dump_json = params.model_dump_json()
    config.vocareum_cookies_path.write_text(model_dump_json)
    api_browser.browser.stop()
else:
    params = load_vocareum_params(config.vocareum_cookies_path)

vocareum_api = VocareumApi(params)
response = vocareum_api.get_aws_status()
print(response)
