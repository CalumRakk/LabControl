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

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"


class Browser(metaclass=SingletonMeta):
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.context = self.browser.new_context(user_agent=user_agent)
        add_cookies(self.context)
        self.status = StatusInstance.Stopped

    @property
    def current_page(self) -> Page:
        if self.context.pages == []:
            config = Config()
            awsacademy_lab_url = config["URLs"]["awsacademy_lab_url"]
            page = self.context.new_page()
            if awsacademy_lab_url == "":
                page.goto(AWSACADEMY_URL)
            else:
                page.goto(awsacademy_lab_url)
        return self.context.pages[-1]

    def _load_awsacademy(self) -> FrameLocator:
        """
        Inicia session (si se especifica) y carga la pagina de AWS Academy Learner Lab
        """
        config = Config()
        awsacademy_lab_url = config["URLs"]["awsacademy_lab_url"]
        page = self.current_page

        if awsacademy_lab_url in page.url and awsacademy_lab_url != "":
            return page

        if is_login(page):
            self.login(*config.get_credentials())

        if AWSACADEMY_URL not in page.url:
            page.goto(AWSACADEMY_URL)

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
        if awsacademy_lab_url == "":
            href = locate_instance.get_attribute("href")
            config["URLs"]["awsacademy_lab_url"] = urljoin(page.url, href)
            config.save()
        locate_instance.click()

        time.sleep(5)
        return page

    def __start_lab(self, page: Page) -> StatusLab:
        # La pagina del laboratorio cargado tiene los dos botones para iniciar o detener el laboratorio.
        # Cuando un laboratorio es detenido, las instancias de AWS Academy Learner Lab se detienen.

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
        return getattr(StatusLab, title_split)

    # def _load_lab_page(self, force_load: bool = True) -> Page:
    #     config = Config()

    #     page = self.context.new_page()
    #     page_url = config["vocareum"]["url"]
    #     page.goto(page_url)

    #     if force_load and is_login(page):
    #         username = config["account"]["username"]
    #         password = config["account"]["password"]
    #         self.login(username, password)
    #     return page

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

    def load_aws(self, force_load: bool = True, cache=False):
        if cache and hasattr(self, "_page_aws"):
            return getattr(self, "_page_aws")
        else:
            self.status = StatusInstance.Pending

            page_lab = self._load_awsacademy()
            status = self.__get_status_lab(page_lab)
            if status.is_off:
                self.__start_lab(page_lab)

            frame = self.__get_lab_frame(page_lab)

            with self.context.expect_page() as result_page:
                locator = frame.locator("xpath=//span[@onclick='launchAws()']")
                locator.wait_for()
                locator.click()

            new_page = result_page.value
            new_page.wait_for_load_state()
            return new_page

            print("status", status)

            # with self.context.expect_page() as result_page:
            #     page_lab.query_selector("#vmBtn").click()

            # new_page = result_page.value
            # new_page.wait_for_load_state()
            # page_lab.close()

            # # carga finalmente el panel de instancias a una localidad especifica
            # us_west_oregon_url = config["aws"]["us_west_oregon_url"]
            # new_page.goto(us_west_oregon_url)

            # self.status = StatusInstance.Running
            # setattr(self, "_page_aws", new_page)
            # return new_page

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


def add_cookies(context: BrowserContext):
    """Agrega las cookies locales al contexto (navegador)"""
    config = Config()
    path_cookies_browser = config["filepath"]["cookies_browser"]
    path = Path(path_cookies_browser)
    if path.exists():
        cookies_list = json.loads(path.read_text())
        context.add_cookies(cookies=cookies_list)


def is_login(page: Page) -> bool:
    """Devuelve True si la url de la pagina contine la palabra 'login'"""
    if "login" in page.url.lower():
        return True
    return False
