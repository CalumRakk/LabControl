from enum import Enum


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
