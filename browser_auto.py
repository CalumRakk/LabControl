import time
from lxml import html
from playwright.sync_api import sync_playwright
from playwright._impl._errors import TimeoutError
import random
from cloudAuto.utils import sleep_program
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)
URL_LOGIN = "https://awsacademy.instructure.com/login/canvas"
URL_LAB = "https://awsacademy.instructure.com/courses/51160/modules/items/5197438"
delay = lambda: random.uniform(200, 500)
get_currentUrl = lambda page: page.evaluate("() => {return window.location.href;}")


def login_and_get_cookies(username, password, headless=True) -> list[dict]:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        )
        page = context.new_page()
        logger.info("Navegador web cargado.")

        page.goto(URL_LOGIN)
        logger.info(f"Se cargó la siguiente URL: {get_currentUrl(page)}")

        logger.info("Tipeando las credenciales en el formulario de login de la página.")
        page.keyboard.type(username, delay=delay())
        page.keyboard.press("Tab")
        page.keyboard.type(password, delay=delay())
        page.query_selector("[type='submit']").click()
        logger.info("Se envió el formulario de inicio de sesión.")

        # Una pequeña espera antes de visitar la URL de la carga de laboratorio.
        logger.info("Esperando antes de visitar la URL de carga de laboratorio.")
        sleep_program(random.randint(1, 10))
        page.goto(URL_LAB)
        status = page.evaluate("() => {return document.readyState;}")
        logger.info(
            f"Se cargó la siguiente URL: {get_currentUrl(page)} con status: {status}"
        )
        sleep_program(random.randint(1, 10))
        page.query_selector("[type='submit']").click()
        logger.info("Haciendo clic en el botón 'Cargar Laboratorio'.")

        logger.info("Esperando a que haya dos pestañas antes de continuar...")
        seg = 0
        while len(context.pages) < 2:
            seg += 1
            time.sleep(1)
            if seg >= 15:
                logger.info("Haciendo clic en el botón 'Cargar Laboratorio'.")
                try:
                    element = page.query_selector("[type='submit']")
                    element.click()
                except TimeoutError:
                    logger.error(
                        "Error TimeoutError al hacer clic en el botón 'Cargar Laboratorio'."
                    )
                seg = 0

        logger.info(
            "Esperando a que se complete la carga de la página de la nueva pestaña."
        )
        NewPageReturned = context.pages[1]
        while True:
            status = NewPageReturned.evaluate("() => {return document.readyState;}")
            if status == "complete":
                break
            time.sleep(1)
        logger.info("Se completó la carga del laboratorio.")

        cookies = context.cookies()
        logger.info("Devolviendo las cookies del navegador.")
        return cookies


username, password = Path("user").read_text().split(":")
cookies_browser = login_and_get_cookies(
    username=username,
    password=password,
)
Path("cookies_browser.json").write_text(json.dumps(cookies_browser))
