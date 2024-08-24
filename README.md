## LabAWS

**LabAWS** es un paquete que permite iniciar un laboratorio de AWS de manera sencilla y mantener la sesión activa automáticamente sin intervención manual. Con solo unas pocas líneas de código.

### Uso

El siguiente ejemplo muestra cómo iniciar el laboratorio de AWS utilizando el paquete **LabAWS**:

```python
from cloudAuto import LabAWS

lab = LabAWS()
response = lab.start()
```
