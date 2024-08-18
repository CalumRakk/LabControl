import time
from urllib.parse import urljoin

from playwright.sync_api import Page, FrameLocator


from ... import Config
from ...constants import ActionsInstance, StatusInstance, StatusLab
from .constants import *


class Methods:

    def _load_awsacademy(self, page: Page) -> FrameLocator:
        """
        Inicia session (si es necesario) y carga la pagina de AWS Academy Learner Lab
        """
        # config = Config()
        # awsacademy_lab_url = config["URLs"]["awsacademy_lab_url"]
        # page = self.current_page

        # if awsacademy_lab_url in page.url and awsacademy_lab_url != "":
        #     return page

        # if is_login(page):
        #     self.login(*config.get_credentials())

        # if AWSACADEMY_URL not in page.url:
        #     page.goto(AWSACADEMY_URL)

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
        time.sleep(5)
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


def is_login(page: Page) -> bool:
    """Devuelve True si la url de la pagina contine la palabra 'login'"""
    if "login" in page.url.lower():
        return True
    return False
