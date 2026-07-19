# Primer entregable: conexión, exploración y limpieza

## Objetivo del avance

Demostrar desde la terminal que Python puede conectarse a una URL pública de Computrabajo Perú, explorar la estructura del HTML, extraer campos básicos y aplicar reglas iniciales de limpieza.

## Alcance implementado

1. Construcción dinámica de la URL a partir del puesto buscado.
2. Solicitud HTTP con encabezados, timeout y validación de respuesta.
3. Conteo de etiquetas, clases y tarjetas detectadas.
4. Extracción de título, empresa, ubicación y URL.
5. Persistencia de datos crudos en JSON.
6. Limpieza de espacios, títulos vacíos y duplicados con Pandas.
7. Persistencia de datos limpios en CSV.
8. Pruebas sencillas con funciones y `assert`, ejecutables sin conexión a internet.

## Enfoque de programación

Este avance utiliza programación secuencial y funciones. La programación orientada a objetos se reserva para una etapa posterior, cuando el crecimiento del proyecto justifique organizar estado y comportamiento en clases.

## Evidencias para la exposición

- Comando de ejecución y estado HTTP 200.
- Resumen JSON de la estructura HTML.
- Cantidad de tarjetas detectadas y registros extraídos.
- Comparación entre datos crudos y limpios.
- Reporte de filas descartadas y duplicados.
- Resultado de cinco pruebas con estado `OK`.

## Fuera del alcance

Este avance todavía no incluye detalles completos, habilidades, dashboard, gráficos, Streamlit ni despliegue. Esas funcionalidades corresponden a entregables posteriores.
