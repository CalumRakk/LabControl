## LabAWS

**LabAWS** es un paquete para iniciar y gestionar el laboratorio de AWS con unas pocas líneas de código.

## Configuración

Antes de utilizar **LabAWS**, hay que crear un archivo de configuración llamado ´config.ini´ con las siguientes secciones:

```ini
[account]
username = 6XXXXX-XXX0
password = nXXXXXXXW
```

- **username**: Tu nombre de usuario para acceder al laboratorio.
- **password**: Tu contraseña para acceder al laboratorio.

## Uso

Para iniciar el laboratorio de AWS utilizando el paquete **LabAWS**, sigue estos pasos:

```python
from labcontrol import LabAWS

lab = LabAWS()
lab.start()

```
