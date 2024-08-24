from cloudAuto import LabAWS
from cloudAuto.api_aws.constants import LabStatus

lab = LabAWS()
if lab.status == LabStatus.ready:
    print("El laboratorio está listo para usar.")
    lab.stop()
