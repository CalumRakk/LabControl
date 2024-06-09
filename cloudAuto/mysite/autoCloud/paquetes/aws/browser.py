from playwright.sync_api import (
    sync_playwright,
    expect,
    Page,
    BrowserContext,
    FrameLocator,
)
from pathlib import Path
import json
from autoCloud import Config
from autoCloud.constants import ActionsInstance, StatusInstance
from autoCloud.utils import sleep_program
import random
from autoCloud.singleton import SingletonMeta

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"


class Browser(metaclass=SingletonMeta):
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.context = self.browser.new_context(user_agent=user_agent)
        add_cookies(self.context)
        self.status = StatusInstance.Stopped

    def _load_lab_page(self, force_load: bool = True) -> Page:
        config = Config()

        page = self.context.new_page()
        lab_url = config["vocareum"]["labs_url"]
        page.goto(lab_url)

        if force_load and is_login(page):
            username = config["account"]["username"]
            password = config["account"]["password"]
            self.login(username, password)
        return page

    def login(self, username, password, save=True):
        """Inicia sesión y carga el laboratorio"""
        config = Config()
        canvas_login_url = config["awsacademy"]["canvas_login_url"]

        page = self.context.new_page()
        page.goto(canvas_login_url)

        # Iniciar sesión
        delay = lambda: random.uniform(200, 500)
        page.keyboard.type(username, delay=delay())
        page.keyboard.press("Tab")
        page.keyboard.type(password, delay=delay())
        page.query_selector("[type='submit']").click()

        sleep_program(random.randint(1, 10))

        # Carga el laboratorio
        module_url = config["awsacademy"]["module_url"]
        page.goto(module_url)
        sleep_program(random.randint(1, 10))
        with self.context.expect_page() as result_page:
            page.query_selector("[type='submit']").click()

        new_page = result_page.value
        new_page.wait_for_load_state()
        sleep_program(random.randint(1, 10))
        cookies = self.context.cookies()
        new_page.close()
        if save:
            path = config["filepath"]["cookies_browser"]
            Path(path).write_text(json.dumps(cookies))

    def load_aws(self, force_load: bool = True, cache=False):
        if cache and hasattr(self, "_page_aws"):
            return getattr(self, "_page_aws")
        else:
            config = Config()
            page_lab = self._load_lab_page(force_load=force_load)

            with self.context.expect_page() as result_page:
                page_lab.query_selector("#vmBtn").click()

            new_page = result_page.value
            new_page.wait_for_load_state()
            page_lab.close()

            # carga finalmente el panel de instancias a una localidad especifica
            us_west_oregon_url = config["aws"]["us_west_oregon_url"]
            new_page.goto(us_west_oregon_url)

            setattr(self, "_page_aws", new_page)
            return new_page

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
    """Agrega unas cookies especificas al contexto (navegador)"""
    config = Config()
    path_cookies_browser = config["filepath"]["cookies_browser"]
    cookies_list = json.loads(Path(path_cookies_browser).read_text())
    context.add_cookies(cookies=cookies_list)


def is_login(page: Page) -> bool:
    """Devuelve True si se está dentro de la pagina de inicio de sesión de Vocareum"""
    # TODO: verificar sin tener que refrescar

    config = Config()
    login_page_url = config["vocareum"]["login_url"]
    page.reload()
    if page.url == login_page_url:
        return True
    return False
