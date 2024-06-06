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


STATUS_SPANISH = {
    StatusInstance.Stopped: "Detenida",
    StatusInstance.Pending: "Pendiente",
    StatusInstance.Running: "En ejecución",
    StatusInstance.Stopping: "Deteniéndose",
}
