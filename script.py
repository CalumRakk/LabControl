from cloudAuto.paquetes.aws import LabAWS

lab = LabAWS()
lab.startaws()
get_status = lab.getawsstatus()

print(get_status)
