import logging
import time
from pathlib import Path
from typing import Optional, Union

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class DriverManager(metaclass=SingletonMeta):
    def __init__(
        self,
        chrome_profile_path: Optional[Union[Path, str]] = None,
        headless: bool = False,
    ):
        self.chrome_profile_path = chrome_profile_path
        self.headless = headless
        self._driver = None

    def _load_driver(self) -> webdriver.Chrome:
        """Inicializa el driver si no existe todavía."""

        logger.info("Iniciando driver...")
        options = webdriver.ChromeOptions()

        if self.chrome_profile_path:
            options.add_argument("--allow-profiles-outside-user-dir")
            options.add_argument("--user-data-dir=" + str(self.chrome_profile_path))
        if self.headless:
            options.add_argument("--headless=new")

        options.add_argument("--disable-extensions")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-infobars")
        options.add_argument("--no-first-run")
        options.add_argument("--disable-session-crashed-bubble")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")
        options.add_argument("--no-sandbox")
        options.add_argument("--lang=en-US")

        service = ChromeService(executable_path=ChromeDriverManager().install())
        self._driver = webdriver.Chrome(service=service, options=options)
        self._driver.set_window_size(800, 600)
        logger.info("Driver iniciado.")
        return self._driver

    @property
    def driver(self) -> webdriver.Chrome:
        """Devuelve el driver, inicializándolo si es necesario."""
        if self._driver is not None:
            return getattr(self, "_driver")

        driver = self._load_driver()

        setattr(self, "_driver", driver)
        return getattr(self, "_driver")

    def stop(self):
        """Cierra y limpia el driver."""
        if self._driver:
            logger.info("Cerrando driver...")
            self._driver.quit()
            self._driver = None

    def navigate_to_url(self, url: str):
        if url not in self.driver.current_url:
            self.driver.get(url)
            time.sleep(5)
