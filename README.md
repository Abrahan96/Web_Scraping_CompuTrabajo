# Analizador de ofertas de Computrabajo - Entregable 1

Esta rama contiene exclusivamente el primer avance académico: conexión a la URL, exploración del HTML, extracción inicial, limpieza básica y pruebas desde terminal.

El código utiliza **funciones y programación secuencial**, igual que los ejemplos iniciales del curso. No utiliza programación orientada a objetos.

## Estructura

```text
main.py                    Pasos principales ejecutados en orden
src/conexion.py            Funciones de URL y solicitud HTTP
src/exploracion.py         Funciones de BeautifulSoup
src/limpieza.py            Funciones de limpieza con Pandas
tests/pruebas_terminal.py  Pruebas sencillas con assert
data/raw/               Muestra de datos crudos
data/processed/         Muestra limpia
docs/ENTREGABLE_1.md    Alcance y evidencias
docs/GUIA_SUSTENTACION.md Guía para explicar el código
```

## Instalación

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Ejecución en terminal

```powershell
python main.py
```

El programa solicitará el puesto en la terminal:

```text
Escribe el puesto que deseas buscar [analista de datos]:
```

Puedes escribir, por ejemplo, `técnico de farmacia`. Si presionas Enter sin escribir, se utilizará `analista de datos`.

La terminal mostrará:

- URL consultada y estado HTTP.
- Tamaño de la respuesta.
- Resumen de etiquetas y clases HTML.
- Cantidad de ofertas extraídas.
- Reporte de limpieza.
- Vista previa del dataset.

## Pruebas

```powershell
python -m tests.pruebas_terminal
```

Las pruebas usan funciones, instrucciones `assert` y un HTML reducido en `tests/fixtures/listado.html`. No necesitan conectarse a Computrabajo.

La cantidad de páginas se mantiene en una variable sencilla dentro de `main.py` para este primer avance.

## Archivos generados

```text
data/raw/ultima_extraccion.json
data/processed/ofertas_limpias.csv
```

## Limitaciones de este avance

No incluye extracción de descripciones, análisis de habilidades, Data App, visualizaciones ni despliegue. Esas funcionalidades permanecen en la rama `main` como referencia del proyecto final.
