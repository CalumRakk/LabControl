from enum import Enum


class StatusInstance(Enum):
    Stopped = "Stopped"
    Pending = "Pending"
    Running = "Running"
    Stopping = "Stopping"
    Unknown = "Unknown"

    @property
    def is_on(self) -> bool:
        return self in [StatusInstance.Running]

    @property
    def is_off(self) -> bool:
        return not self in [StatusInstance.Running]

    @property
    def translate(self) -> str:
        return STATUS_SPANISH[self]


class StatusLab(Enum):
    Terminated = "Terminated"
    Initializing = "Initializing"
    In_Creation = "In Creation"
    Ready = "Ready"
    Shutting_down = "Shutting down"

    @property
    def is_on(self) -> bool:
        return self in [StatusLab.Ready]

    @property
    def is_off(self) -> bool:
        return not self in [StatusLab.Ready]

    @property
    def translate(self) -> str:
        return STATUS_LAB_SPANISH[self]


STATUS_SPANISH = {
    StatusInstance.Stopped: "Detenida",
    StatusInstance.Pending: "Pendiente",
    StatusInstance.Running: "En ejecución",
    StatusInstance.Stopping: "Deteniéndose",
    StatusInstance.Unknown: "Desconocido",
}

STATUS_LAB_SPANISH = {
    StatusLab.Terminated: "Terminada",
    StatusLab.Initializing: "Iniciando",
    StatusLab.In_Creation: "En Creación",
    StatusLab.Ready: "Listo",
    StatusLab.Shutting_down: "Apagando",
}
