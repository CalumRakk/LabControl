from cloudAuto.paquetes.aws import LabAWS
from cloudAuto.paquetes.aws.constants import LabStatus

lab = LabAWS()
if lab.status == LabStatus.ready:
    print("El laboratorio está listo para usar.")
    lab.stop()
