## Auto

El paquete auto se utiliza para mantener activo siempre el laboratorio de AWS y en consecuencia evitar que las instancias EC2 de AWS se apaguen despues de 4 horas.

Solo basta con llamar a la clase Auto del modulo auto y usar el método start()

```python
from auto import Auto

auto= Auto()
auto.start()

```
