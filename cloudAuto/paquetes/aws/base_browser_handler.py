import random
import json
from pathlib import Path
import time
import re
from urllib.parse import urljoin, parse_qs

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
from .constants import *

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"


class Properties:
    def __init__(self, headless=False):
        self.headless = headless
        self.status = BrowserStatus.Stopped
        self.pc_status = PCStatus.Unknown

    @property
    def playwright(self):
        if not hasattr(self, "_playwright"):
            self._playwright = sync_playwright().start()
        return self._playwright

    @property
    def browser(self):
        if not hasattr(self, "_browser"):
            self._browser = self.playwright.chromium.launch(headless=False)
        return self._browser

    @property
    def context(self) -> BrowserContext:
        if not hasattr(self, "_context"):
            self.status = StatusInstance.Running
            self._context = self.browser.new_context(user_agent=user_agent)
            add_cookies(self.context)
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


class Methods(Properties):
    def __init__(self, headless=False):
        super().__init__(headless=headless)

    def _load_awsacademy(self) -> FrameLocator:
        """
        Dirige al navegador hacia el panel canvas de AWS Academy.
        - Inicia session si es necesario.
        """
        config = Config()
        # awsacademy_lab_url = config["URLs"]["awsacademy_lab_url"]
        # page = self.current_page

        # if awsacademy_lab_url in page.url and awsacademy_lab_url != "":
        #     return page

        # if is_login(page):
        #     self.login(*config.get_credentials())

        # if AWSACADEMY_URL not in page.url:
        #     page.goto(AWSACADEMY_URL)
        page = self.go_url(AWSACADEMY_URL)
        if is_login(page):
            self._login(*config.get_credentials())

        # Clickea en el boton de AWS Academy Learner Lab ['USER']
        locate_instance = page.locator(f"xpath=//a[@class='ic-DashboardCard__link']")
        locate_instance.wait_for()
        locate_instance.click()

        # click al menu 'Modulos'
        locate_instance = page.locator(f"xpath=//a[@class='modules']")
        locate_instance.wait_for()
        locate_instance.click()

        # click al boton 'Iniciar el Laboratorio de aprendizaje de AWS Academy'
        # TODO : confirmar si el ID cambia si se usa otra cuenta.
        locate_instance = page.locator(
            f"xpath=//div[@id='context_module_content_827099']//a[@class='ig-title title item_link']"
        )
        locate_instance.wait_for()
        # guarda en config la URL del laboratorio
        # if awsacademy_lab_url == "":
        #     href = locate_instance.get_attribute("href")
        #     config["URLs"]["awsacademy_lab_url"] = urljoin(page.url, href)
        #     config.save()

        locate_instance.click()

        self._wait_for_lab_load(page)

        return page

    def _wait_for_lab_load(self, page: Page, save=True):
        config = Config()
        # panel2-iframe
        frame = page.locator("xpath=//div[@id='content']").frame_locator("iframe").first

        element = frame.locator("xpath=//div[@id='launchclabsbtn']")
        element.wait_for()

        if save:
            # TODO: corregir el sobreescribiendo de archivo de cookies
            cookies_vocareum = self.context.cookies(VOCAREUM_URL)
            path = config["filepath"]["cookies_vocareum"]
            Path(path).write_text(json.dumps(cookies_vocareum))

            # guarda varios datos claves obtenidos de la URL insertada en el iframe
            path = Path(config["filepath"]["data_vocareum"])
            if not path.exists():
                reset_element = frame.locator("xpath=//div[@id='ResetAssignmentBtn']")
                reset_attr_onclick = reset_element.get_attribute("onclick")
                query_string = re.search(r"(?<=').*(?=')", reset_attr_onclick).group()
                data = {}
                for key, value in parse_qs(query_string.split("?")[1]).items():
                    data.update({key: value[0]})
                path.write_text(json.dumps(data))

        return True

    def _login(self, username, password, save=True):
        """Inicia sesión y carga el laboratorio"""
        config = Config()
        page = self.go_url(AWSACADEMY_LOGIN_URL)

        if is_login(page) is False:
            return page

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

    def go_url(self, url) -> Page:
        """Metodo para ir a una URL"""

        page = self.current_page
        if not (isinstance(url, str) and url.startswith("http")):
            return False

        if url in page.url:
            return page

        page.goto(url)
        self.last_url = url
        return page

    def __start_lab(self, page: Page) -> StatusLab:
        """click al boton "Start Lab" de la pagina del laboratorio."""
        # La pagina del laboratorio cargado tiene dos botones: para iniciar o detener el laboratorio.
        # Cuando un laboratorio es detenido, las instancias de AWS se detienen.

        frame = self.__get_lab_frame(page)
        locator = frame.locator("xpath=//div[@id='launchclabsbtn']")
        locator.wait_for()
        locator.click()

        return self.__get_status_lab(page)

    def __get_lab_frame(self, page: Page) -> FrameLocator:
        frame = page.frame_locator(".tool_launch")
        return frame

    def __get_status_lab(self, page: Page) -> StatusInstance:
        page.reload()
        time.sleep(5)

        frame = self.__get_lab_frame(page)

        locator = frame.locator("xpath=//i[@id='vmstatus']")
        locator.wait_for()
        title = locator.get_attribute("title")
        title_split = title.split(" ")[-1]
        return StatusLab.string_to_status(title_split)

    def _select_instance(self, page: Page, instance_id) -> FrameLocator:
        """Selecciona la fila de la instancia si no está seleccionada"""
        frame = page.frame_locator("#compute-react-frame")

        locate_instance = frame.locator(
            f"xpath=//tr[.//a[contains(text(),'{instance_id}')]]/td[1]/span/label"
        )

        if locate_instance.is_checked() is False:
            locate_instance.click()
        return frame

    def _apply_action_instance(self, frame: FrameLocator, action: ActionsInstance):
        # Abre el menu de acciones de la instancia
        if isinstance(action, ActionsInstance) is False:
            raise ValueError("action debe ser una instancia de ActionsInstance")

        # Abre el menu de acciones de la instancia
        frame.locator(
            f"xpath=//div[@class='awsui_dropdown-trigger_sne0l_lqyym_193']/button"
        ).first.click()

        # Hace clic en el botón de la accion especificada
        locate_action = frame.locator(f"xpath=//li[@data-testid='{action.item}']")
        locate_action.click()

        # click en confirmación la accion si la action es Stop
        if action == ActionsInstance.Stop:
            frame.locator(
                "xpath=//button[@data-id='confirmation-modal-primary-btn']"
            ).click()


class BaseBrowserHandler(property, Methods):
    def __init__(self, headless=False):
        super().__init__(headless=headless)


def is_login(page: Page) -> bool:
    """Devuelve True si la url de la pagina contine la palabra 'login'"""
    if "login" in page.url.lower():
        return True
    return False


def add_cookies(context: BrowserContext):
    """Agrega las cookies locales al contexto (navegador)"""
    config = Config()
    path_cookies_browser = config["filepath"]["cookies_browser"]
    path = Path(path_cookies_browser)
    if path.exists():
        cookies_list = json.loads(path.read_text())
        context.add_cookies(cookies=cookies_list)
