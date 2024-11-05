from playwright.sync_api import Page

from ..constants import ActionsInstance, StatusInstance, StatusLab
from labcontrol.singleton import SingletonMeta
from .base_browser_handler import BaseBrowserHandler


class Browser(BaseBrowserHandler, metaclass=SingletonMeta):
    def __init__(self, headless=True):
        super().__init__(headless=headless)

    @classmethod
    def stop(cls, instance):
        """Detiene el navegador y lo elimina de las instancia del singleton para que se pueda volver a intanciar como un nuevo objeto."""
        if cls in cls._instances:
            r = cls._instances.pop(cls)
            del r
            instance.playwright.stop()

    def load_aws(self):
        self._load_awsacademy()

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
