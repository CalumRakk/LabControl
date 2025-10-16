from ctypes import cast
import requests
import logging
from labcontrol.api.parser import SeleniumCookie, cookies_to_requests, cookies_to_selenium
from urllib.parse import unquote
from lxml import html
logger= logging.getLogger(__name__)

headers = {
    "accept": "*/*",
    "accept-language": "es-419,es;q=0.9",
    "priority": "u=1, i",
    "sec-ch-ua": '"Not;A=Brand";v="24", "Chromium";v="128"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}
class LabAWSHttpApi():

    def _get_initial_cookies(self)-> dict[str,str]:
        """Obtiene las cookies iniciales necesarias para el login. Las cookies devueltas estan compactas: {cookie_name: cookie_value}"""
        url= "https://awsacademy.instructure.com/login/canvas"
        response= requests.get(url, headers=headers)
        return cookies_to_requests(response.headers.get("Set-Cookie", ""))
    
    def _get_login_cookies(self, initial_cookies: dict[str,str]):
        data = {
            'utf8': '✓',
            'authenticity_token':  unquote( initial_cookies["_csrf_token"]),
            'redirect_to_ssl': '1',
            'pseudonym_session[unique_id]': self.unique_id,
            'pseudonym_session[password]': self.password,
            'pseudonym_session[remember_me]': '0',
        }

        response = requests.post('https://awsacademy.instructure.com/login/canvas', cookies=initial_cookies, headers=headers, data=data)
        
        assert len(response.history) == 3, "Login failed, check your credentials"

        responses= [i for i in response.history]
        response_login_canvas= responses[0]
        response_sso_vancaslms= responses[1]
        response_login_succes= responses[2]
        return cookies_to_requests(response_login_canvas.headers.get("Set-Cookie", ""))
    def _validate_and_get_final_cookies(self, login_cookies: dict[str,str]):
        """Devuelve las cookies finales si el login fue exitoso. Las cookies devuelvas tienen un formato para selenium."""
        params = {
            'login_success': '1',
        }        
        response = requests.get('https://awsacademy.instructure.com/login/canvas', params=params, cookies=login_cookies, headers=headers)

        if response.status_code == 200:
            logger.info("Login successful")
            cookies_validated= cookies_to_selenium(response.headers.get("Set-Cookie","",), domain=".awsacademy.instructure.com")
            return cookies_validated

        logger.error("Login failed")
        raise Exception("Login failed")

    def login(self, unique_id: str, password: str):
        self.unique_id = unique_id
        self.password = password

        initial_cookies= self._get_initial_cookies()
        login_cookies= self._get_login_cookies(initial_cookies)        
        cookies_validated= self._validate_and_get_final_cookies(login_cookies)
        # cookies_validated_compact= {k: v["value"] for k, v in cookies_validated.items()}
        return cookies_validated
    def is_valid_cookie(self, cookies: list[SeleniumCookie])-> bool:
        url= "https://awsacademy.instructure.com/profile/settings"
        
        cookie_dict : dict = {i["name"]: i["value"] for i in cookies}
        response= requests.get(url, headers=headers, cookies=cookie_dict)

        root= html.fromstring(response.text)
        
        full_name_element=  root.find(".//span[@class='full_name display_data']")
        return full_name_element is not None