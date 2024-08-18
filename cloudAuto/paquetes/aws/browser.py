import random
import json
from pathlib import Path
import time
from urllib.parse import urljoin

from playwright.sync_api import (
    sync_playwright,
    expect,
    Page,
    BrowserContext,
    FrameLocator,
)


from ... import Config
from ...constants import ActionsInstance, StatusInstance, StatusLab
from ...utils import sleep_program
from ...singleton import SingletonMeta
from .constants import *
from .methods import Methods

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"


class Browser(Methods, metaclass=SingletonMeta):
    def __init__(self, headless=False):
        self.headless = headless
        self.status = BrowserStatus.Stopped
        self.pc_status = PCStatus.Unknown

    @classmethod
    def stop(cls, instance):
        """Detiene el navegador y lo elimina de las instancia del singleton para que se pueda volver a intanciar como un nuevo objeto."""
        if cls in cls._instances:
            r = cls._instances.pop(cls)
            del r
            instance.playwright.stop()

    @property
    def playwright(self):
        if not hasattr(self, "_playwright"):
            self._playwright = sync_playwright().start()
        return self._playwright

    @property
    def browser(self):
        if not hasattr(self, "_browser"):
            self._browser = self.playwright.chromium.launch(headless=False)
            add_cookies(self.context)
        return self._browser

    @property
    def context(self) -> BrowserContext:
        if not hasattr(self, "_context"):
            self.status = StatusInstance.Running
            self._context = self.browser.new_context(user_agent=user_agent)
        return self._context

    @property
    def current_page(self) -> Page:
        if self.context.pages == []:
            # config = Config()
            # awsacademy_lab_url = config["URLs"]["awsacademy_lab_url"]

            page = self.context.new_page()
            return page
            # if awsacademy_lab_url == "":
            #     page.goto(AWSACADEMY_URL)
            # else:
            #     page.goto(awsacademy_lab_url)
        return self.context.pages[-1]

    @property
    def last_url(self) -> str:
        """La URL especificada por el usuario."""
        return getattr(self, "_last_url")

    @last_url.setter
    def last_url(self, value: str):
        self._last_url = value

    def login(self, username, password, save=True):
        """Inicia sesión y carga el laboratorio"""
        config = Config()
        page = self.current_page

        if page.url != AWSACADEMY_LOGIN_URL:
            page.goto(AWSACADEMY_LOGIN_URL)

        # Iniciar sesión
        delay = lambda: random.uniform(200, 500)
        page.keyboard.type(username, delay=delay())
        page.keyboard.press("Tab")
        page.keyboard.type(password, delay=delay())
        page.query_selector("[type='submit']").click()

        sleep_program(random.randint(1, 10))

        # # Carga el laboratorio
        # module_url = config["awsacademy"]["module_url"]
        # page.goto(module_url)
        # sleep_program(random.randint(1, 10))
        # with self.context.expect_page() as result_page:
        #     page.query_selector("[type='submit']").click()

        # new_page = result_page.value
        # new_page.wait_for_load_state()
        # sleep_program(random.randint(1, 10))
        cookies = self.context.cookies()
        if save:
            path = config["filepath"]["cookies_browser"]
            Path(path).write_text(json.dumps(cookies))

    def load_aws(self):
        # self.go_url(AWSACADEMY_URL)

        page_lab = self._load_awsacademy()
        status = self.__get_status_lab(page_lab)
        if status.is_off:
            self.__start_lab(page_lab)

        frame = self.__get_lab_frame(page_lab)

        # click sobre el boton AWS para obtener la pagina de AWS con credenciales.
        with self.context.expect_page() as result_page:
            locator = frame.locator("xpath=//span[@onclick='launchAws()']")
            locator.wait_for()
            locator.click()

        new_page = result_page.value
        new_page.wait_for_load_state()
        return new_page

    def get_status_instance(self, page: Page, instance_id) -> StatusInstance:
        # no es necesario actualizar la pagina
        frame = self._select_instance(page, instance_id)

        locate = frame.locator(
            f"xpath=//tr[.//a[contains(text(),'{instance_id}')]]//button[starts-with(@data-analytics, 'instances-1-click-state-filter-')][1]"
        )
        value = locate.get_attribute("data-analytics")
        status_text = value.split("-")[-1]
        status_text.capitalize()
        return getattr(StatusInstance, status_text.capitalize())

    def set_action_instance(
        self, page: Page, instance_id: str, action: ActionsInstance
    ):
        frame = self._select_instance(page, instance_id)
        self._apply_action_instance(frame, action)

    def go_url(self, url) -> Page:
        """Metodo para ir a una URL"""

        page = self.current_page
        if not (isinstance(url, str) and url.startswith("http")):
            return False

        if url in page.url:
            return page

        page.goto(url)
        self.last_url = url
        return True


def add_cookies(context: BrowserContext):
    """Agrega las cookies locales al contexto (navegador)"""
    config = Config()
    path_cookies_browser = config["filepath"]["cookies_browser"]
    path = Path(path_cookies_browser)
    if path.exists():
        cookies_list = json.loads(path.read_text())
        context.add_cookies(cookies=cookies_list)
