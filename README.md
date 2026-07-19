# Analizador de ofertas de Computrabajo - Entregable 1

Esta rama contiene exclusivamente el primer avance académico: conexión a la URL, exploración del HTML, extracción inicial, limpieza básica y pruebas desde terminal.

## Estructura

```text
main.py                 Orquestación para terminal
src/conexion.py         Construcción de URL y solicitud HTTP
src/exploracion.py      Exploración HTML y extracción de tarjetas
src/limpieza.py         Limpieza y reporte con Pandas
tests/                  Pruebas sin dependencia de internet
data/raw/               Muestra de datos crudos
data/processed/         Muestra limpia
docs/ENTREGABLE_1.md    Alcance y evidencias
```

## Instalación

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Ejecución en terminal

```powershell
python main.py --puesto "analista de datos" --paginas 1
```

La terminal mostrará:

- URL consultada y estado HTTP.
- Tamaño de la respuesta.
- Resumen de etiquetas y clases HTML.
- Cantidad de ofertas extraídas.
- Reporte de limpieza.
- Vista previa del dataset.

## Pruebas

```powershell
python -m unittest discover -s tests -v
```

Las pruebas usan un HTML reducido en `tests/fixtures/listado.html`, por lo que no dependen de la disponibilidad de Computrabajo.

## Archivos generados

```text
data/raw/ultima_extraccion.json
data/processed/ofertas_limpias.csv
```

## Limitaciones de este avance

No incluye extracción de descripciones, análisis de habilidades, Data App, visualizaciones ni despliegue. Esas funcionalidades permanecen en la rama `main` como referencia del proyecto final.
