# Informe del proyecto: Radar Laboral Perú

> Documento base editable. Completar los campos entre corchetes y convertir a Word respetando Arial 11, interlineado simple, A4 y los márgenes indicados en la rúbrica.

## Carátula

- Curso: Lenguaje de Ciencia de Datos II (5481)
- Profesor: [Nombre]
- Ciclo, aula y semestre: [Completar]
- Coordinador: [Completar]
- Integrantes: [Completar]

## 1. Resumen

Radar Laboral Perú es una solución analítica que automatiza la extracción, transformación y visualización de ofertas laborales publicadas en Computrabajo Perú. La aplicación permite consultar un puesto, identificar empresas contratantes y reconocer habilidades técnicas y blandas presentes en las descripciones. El pipeline conserva datos crudos, genera datasets optimizados y calcula indicadores de calidad antes de presentar los resultados en una Data App interactiva.

## 2. Introducción

Las personas que buscan empleo deben revisar numerosas publicaciones para reconocer qué conocimientos exige el mercado. Esta dispersión dificulta priorizar su aprendizaje y comparar oportunidades. El proyecto consolida ofertas recientes en un dashboard explorable y transforma texto no estructurado en información comparable.

## 3. Diagnóstico SEPTE

Desarrollar al menos tres dimensiones con evidencia estadística, legal o noticiosa y notas al pie.

### Variable social

[Incluir evidencia sobre empleabilidad, brechas de habilidades o búsqueda de empleo en Perú.]

### Variable económica

[Incluir indicadores recientes del mercado laboral, empleo formal o demanda ocupacional.]

### Variable tecnológica

[Incluir evidencia sobre digitalización del reclutamiento y demanda de competencias digitales.]

### Oportunidad identificada

Centralizar y resumir requisitos de ofertas públicas permite que postulantes y centros de formación reconozcan tendencias de habilidades con menor esfuerzo manual.

## 4. Objetivos

### Objetivo general SMART

Desarrollar y desplegar, antes de la sesión 13, una Data App en Streamlit que extraiga automáticamente al menos 40 ofertas asociadas a un puesto consultado, capture sus principales atributos, valide su calidad y permita explorar empresas y habilidades mediante filtros y visualizaciones interactivas.

### Objetivos específicos

1. Automatizar la ingesta paginada del listado y detalle de las ofertas, registrando errores y almacenando los datos crudos en JSON.
2. Normalizar, deduplicar y enriquecer las ofertas mediante una taxonomía documentada, generando CSV, Parquet y métricas de calidad.
3. Implementar filtros, indicadores, gráficos y descarga de resultados en una interfaz comprensible y adaptable.

## 5. Justificación

La solución reduce el tiempo necesario para revisar ofertas y convierte descripciones extensas en indicadores comparables. Los beneficiarios directos son postulantes, estudiantes y orientadores laborales. Los beneficiarios indirectos incluyen instituciones educativas que pueden contrastar sus contenidos con habilidades observadas y empresas interesadas en comprender tendencias generales del mercado.

## 6. Definición y alcance

El alcance comprende ingesta web, limpieza, validación, extracción basada en taxonomía, almacenamiento analítico y visualización. No incluye postulación automática, recopilación de datos de candidatos ni modelos predictivos. Los componentes se documentan en el README y en la trazabilidad técnica.

## 7. Productos y entregables

- Código de ingesta, transformación, pipeline y Data App.
- Taxonomía de habilidades.
- Dataset crudo y datasets procesados.
- Reporte de calidad.
- Pruebas automatizadas.
- Evidencia de ejecución o enlace desplegado.

## 8. Conclusiones

Completar después de ejecutar y analizar una muestra final. Máximo tres conclusiones específicas y respaldadas por resultados.

1. [Hallazgo cuantitativo sobre habilidades.]
2. [Hallazgo cuantitativo sobre empresas, ubicación o experiencia.]
3. [Conclusión sobre calidad o aplicabilidad del pipeline.]

## 9. Recomendaciones

1. Actualizar periódicamente la taxonomía y validar manualmente una muestra de resultados.
2. Mantener límites y pausas responsables durante la ingesta.
3. Incorporar otras fuentes solo después de estabilizar y medir la calidad del pipeline actual.

## 10. Glosario

- **Data App:** aplicación orientada a explorar y comunicar datos.
- **ETL:** proceso de extracción, transformación y carga.
- **JobPosting:** esquema de datos estructurados para una oferta laboral.
- **Parquet:** formato columnar optimizado para análisis.
- **Taxonomía:** catálogo controlado de habilidades y sinónimos.
- **Web scraping:** extracción automatizada de información pública de páginas web.

## 11. Bibliografía

[Agregar todas las fuentes SEPTE y referencias técnicas con un estilo de citación consistente.]

## 12. Anexos

- Arquitectura del pipeline.
- Diccionario de datos.
- Reporte de calidad.
- Evidencias de pruebas y despliegue.
