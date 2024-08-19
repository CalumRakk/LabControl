from enum import Enum


# Acciones relacionadas con al panel lab de AWS Academy
class ActionsInstance(Enum):
    Stop = "Stop"
    Start = "Start"
    Reboot = "Reboot"
    Hibernate = "Hibernate"

    @property
    def translate(self) -> str:
        return ACTIONS_SPANISH[self]

    @property
    def item(self) -> str:
        return ACTIONS_ITEMS[self]


ACTIONS_ITEMS = {
    ActionsInstance.Stop: "item-1",
    ActionsInstance.Start: "item-2",
    ActionsInstance.Reboot: "item-3",
    ActionsInstance.Hibernate: "item-4",
}

ACTIONS_SPANISH = {
    ActionsInstance.Stop: "Detener",
    ActionsInstance.Start: "Iniciar",
    ActionsInstance.Reboot: "Reiniciar",
    ActionsInstance.Hibernate: "Hibernar",
}


class Action(Enum):
    startBrowser = "startBrowser"
    startServerMinecraft = "startServerMinecraft"
    stopBrowser = "stopBrowser"
    stopServerMinecraft = "stopServerMinecraft"
    go_to_url = "go_to_url"
    checkTask = "checkTask"
    getStatus = "getStatus"
