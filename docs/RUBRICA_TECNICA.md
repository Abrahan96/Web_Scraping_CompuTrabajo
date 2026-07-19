# Trazabilidad técnica con la rúbrica

## Ingesta automatizada

- Fuente web automatizada mediante `ExtractorComputrabajo`.
- Descubrimiento paginado y extracción individual de detalles.
- Datos estructurados `JobPosting` como fuente primaria.
- Timeout, tres reintentos, espera progresiva y pausas entre solicitudes.
- Errores controlados, advertencias parciales y escritura atómica.
- Persistencia cruda en JSON y procesada en Parquet.

## Transformación y calidad

- Validación de columnas obligatorias y dataset vacío.
- Tratamiento uniforme de textos y valores faltantes.
- Eliminación documentada de duplicados.
- Normalización de tildes, mayúsculas y espacios para reglas analíticas.
- Taxonomía externa de habilidades con sinónimos.
- Reglas de experiencia con precedencia explícita.
- Reporte JSON de cobertura, vacíos y duplicados.

## Data App

- Consulta configurable por puesto, páginas y cantidad de ofertas.
- Filtros por empresa, departamento, experiencia, habilidad y texto.
- Indicadores de volumen y calidad.
- Gráficos interactivos de habilidades y experiencia.
- Tabla con enlaces a las fuentes y descarga en CSV.
- Mensajes diferenciados para búsquedas vacías, fallos y advertencias parciales.

## Despliegue y buenas prácticas

- Dependencias directas y versionadas.
- Separación entre ingesta, transformación, orquestación e interfaz.
- Configuración analítica fuera del código.
- Pruebas unitarias de selectores, datos estructurados, reglas, exportación e interfaz inicial.
- README con instalación, ejecución, arquitectura y uso responsable.

## Evidencias sugeridas para la entrega

1. Captura de una búsqueda completada.
2. Captura de los filtros y gráficos.
3. Copia del reporte de calidad.
4. Resultado de la ejecución de pruebas.
5. Enlace del despliegue o captura de la ejecución local.
