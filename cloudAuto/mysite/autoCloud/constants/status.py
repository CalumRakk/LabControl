from enum import Enum


class StatusInstance(Enum):
    Stopped = "Stopped"
    Pending = "Pending"
    Running = "Running"
    Stopping = "Stopping"

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

    @classmethod
    def string_to_status(cls, status: str) -> "StatusLab":
        if hasattr(cls, status):
            return getattr(cls, status)

        if status == "Creation":
            return StatusLab.In_Creation
        elif status == "down":
            return StatusLab.Terminated

        raise Exception(f"status {status} not found")


STATUS_SPANISH = {
    StatusInstance.Stopped: "Detenida",
    StatusInstance.Pending: "Pendiente",
    StatusInstance.Running: "En ejecución",
    StatusInstance.Stopping: "Deteniéndose",
}

STATUS_LAB_SPANISH = {
    StatusLab.Terminated: "Terminada",
    StatusLab.Initializing: "Iniciando",
    StatusLab.In_Creation: "En Creación",
    StatusLab.Ready: "Listo",
    StatusLab.Shutting_down: "Apagando",
}
