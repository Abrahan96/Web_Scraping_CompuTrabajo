# Radar Laboral Perú

Data App académica que extrae ofertas públicas de Computrabajo Perú, valida su calidad y analiza las habilidades solicitadas para cualquier puesto consultado.

## Funcionalidades

- Ingesta automatizada del listado y detalle de cada oferta.
- Lectura preferente del esquema público `JobPosting` de cada página.
- Reintentos, timeout, límites de consulta y manejo de errores.
- Dataset crudo en JSON y procesado en CSV y Parquet.
- Eliminación de duplicados, normalización y reporte de calidad.
- Taxonomía externa y ampliable de habilidades técnicas, blandas, idiomas y metodologías.
- Dashboard con filtros por empresa, ubicación, experiencia y habilidad.
- Descarga de resultados filtrados.
- Pruebas unitarias sin depender de la web.

## Arquitectura

```text
Computrabajo (listado)
        ↓
URLs de ofertas
        ↓
JobPosting (detalle)
        ↓
data/raw/ultima_busqueda.json
        ↓
limpieza + validación + habilidades
        ↓
CSV + Parquet + reporte de calidad
        ↓
Streamlit
```

La interfaz solo presenta resultados devueltos por la ejecución actual. Si una búsqueda falla, no atribuye el Parquet anterior a la nueva consulta.

## Instalación

Requiere Python 3.11 o superior.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Ejecución

```powershell
python -m streamlit run app/main.py
```

## Pruebas

```powershell
python -m unittest discover -s tests -v
```

## Datos generados

| Archivo | Descripción |
|---|---|
| `data/raw/ultima_busqueda.json` | Respuesta normalizada, aún sin reglas analíticas. |
| `data/processed/ultima_busqueda.csv` | Dataset legible e interoperable. |
| `data/processed/ultima_busqueda.parquet` | Dataset optimizado para análisis. |
| `data/processed/reporte_calidad.json` | Cobertura, vacíos y duplicados eliminados. |

## Configuración de habilidades

La taxonomía está en `config/habilidades.csv`. Cada fila contiene una habilidad canónica, su categoría y sinónimos separados por `|`. Esto permite ampliar la solución sin modificar código Python.

## Uso responsable

El extractor limita páginas y ofertas, espera entre solicitudes y aplica reintentos con espera progresiva. Antes de desplegarlo públicamente se deben revisar y respetar los términos de uso y las políticas vigentes del portal. No se recolectan datos personales de candidatos.

## Documentación académica

- [Trazabilidad con la rúbrica](docs/RUBRICA_TECNICA.md)
- [Plantilla del informe final](docs/INFORME_PROYECTO.md)
