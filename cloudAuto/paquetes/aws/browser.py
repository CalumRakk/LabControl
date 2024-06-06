from playwright.sync_api import sync_playwright, expect, Page, BrowserContext
from pathlib import Path
import json
from cloudAuto import Config
from cloudAuto.utils import sleep_program
import random

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"


class Browser:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.context = self.browser.new_context(user_agent=user_agent)
        add_cookies(self.context)

    def load_lab_page(self, force_load: bool = True) -> Page:
        config = Config()

        page = self.context.new_page()
        lab_url = config["vocareum"]["labs_url"]
        page.goto(lab_url)

        if force_load and is_login(page):
            username = config["account"]["username"]
            password = config["account"]["password"]
            self.login(username, password)

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
        if save:
            path = config["filepath"]["cookies_browser"]
            Path(path).write_text(json.dumps(cookies))


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
