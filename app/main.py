"""Data App interactiva para analizar ofertas de Computrabajo Perú."""

from __future__ import annotations

import os
import sys

import pandas as pd
import plotly.express as px
import streamlit as st


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ingesta import ErrorIngesta, SinOfertasError  # noqa: E402
from src.pipeline import ejecutar_pipeline  # noqa: E402
from src.transformacion import ErrorCalidadDatos  # noqa: E402


st.set_page_config(page_title="Radar Laboral Perú", page_icon="🔎", layout="wide")


def _opciones_ordenadas(serie: pd.Series) -> list[str]:
    return sorted(valor for valor in serie.dropna().astype(str).unique() if valor)


def _csv_descargable(df: pd.DataFrame) -> bytes:
    exportable = df.copy()
    exportable["habilidades_requeridas"] = exportable["habilidades_requeridas"].apply(
        lambda valores: " | ".join(valores)
    )
    return exportable.to_csv(index=False).encode("utf-8-sig")


st.title("🔎 Radar Laboral Perú")
st.caption(
    "Explora empresas, requisitos y habilidades solicitadas en ofertas públicas de Computrabajo Perú."
)

with st.sidebar:
    st.header("Configuración")
    paginas = st.slider("Páginas a consultar", min_value=1, max_value=5, value=2)
    limite_ofertas = st.slider("Máximo de ofertas", 10, 100, 40, step=10)
    st.caption("Una búsqueda amplia tarda más porque consulta el detalle de cada oferta.")

with st.form("formulario_busqueda"):
    col_entrada, col_boton = st.columns([4, 1])
    with col_entrada:
        puesto_buscado = st.text_input(
            "¿Qué puesto deseas analizar?",
            placeholder="Ej. Ingeniero de datos, técnico de farmacia, analista SEO",
        )
    with col_boton:
        st.write("")
        buscar = st.form_submit_button("Analizar mercado", use_container_width=True)

if buscar:
    if not puesto_buscado.strip():
        st.warning("Ingresa un puesto de trabajo antes de iniciar el análisis.")
    else:
        try:
            with st.spinner("Extrayendo y validando ofertas. Esto puede tomar unos segundos..."):
                resultado_nuevo = ejecutar_pipeline(
                    puesto_buscado.strip(),
                    limite_paginas=paginas,
                    limite_ofertas=limite_ofertas,
                )
            st.session_state["resultado_pipeline"] = resultado_nuevo
            st.session_state["ultima_consulta"] = puesto_buscado.strip()
            st.success(f"Análisis completado para “{puesto_buscado.strip()}”.")
        except SinOfertasError as error:
            st.warning(str(error))
        except (ErrorIngesta, ErrorCalidadDatos) as error:
            st.error(f"No fue posible completar el pipeline: {error}")
        except Exception as error:
            st.error(f"Ocurrió un error inesperado: {error}")

resultado = st.session_state.get("resultado_pipeline")
if resultado is None:
    st.info("Realiza una búsqueda para generar el dashboard y el dataset procesado.")
    st.stop()

df = resultado.datos.copy()
consulta = st.session_state.get("ultima_consulta", "consulta anterior")
st.caption(f"Resultados vigentes en pantalla: {consulta}")

if resultado.advertencias:
    with st.expander(f"Advertencias de ingesta ({len(resultado.advertencias)})"):
        for advertencia in resultado.advertencias:
            st.write(f"- {advertencia}")

with st.sidebar:
    st.divider()
    st.header("Filtros del resultado")
    empresas = st.multiselect("Empresa", _opciones_ordenadas(df["empresa"]))
    departamentos = st.multiselect("Departamento", _opciones_ordenadas(df["departamento"]))
    niveles = st.multiselect("Nivel de experiencia", _opciones_ordenadas(df["nivel_experiencia"]))
    habilidades_disponibles = sorted(
        habilidad
        for habilidad in df["habilidades_requeridas"].explode().dropna().unique()
        if habilidad != "No detallado"
    )
    habilidades = st.multiselect("Habilidad", habilidades_disponibles)
    texto_filtro = st.text_input("Buscar en título o descripción")

filtrado = df.copy()
if empresas:
    filtrado = filtrado[filtrado["empresa"].isin(empresas)]
if departamentos:
    filtrado = filtrado[filtrado["departamento"].isin(departamentos)]
if niveles:
    filtrado = filtrado[filtrado["nivel_experiencia"].isin(niveles)]
if habilidades:
    filtrado = filtrado[
        filtrado["habilidades_requeridas"].apply(
            lambda valores: any(habilidad in valores for habilidad in habilidades)
        )
    ]
if texto_filtro.strip():
    patron = texto_filtro.strip()
    filtrado = filtrado[
        filtrado["titulo"].str.contains(patron, case=False, na=False, regex=False)
        | filtrado["descripcion"].str.contains(patron, case=False, na=False, regex=False)
    ]

reporte = resultado.reporte_calidad
col1, col2, col3, col4 = st.columns(4)
col1.metric("Ofertas visibles", len(filtrado), delta=f"de {len(df)} extraídas")
col2.metric("Empresas", filtrado["empresa"].nunique())
col3.metric("Cobertura de detalle", f"{reporte['cobertura_detalle_pct']:.1f}%")
col4.metric("Cobertura de habilidades", f"{reporte['cobertura_habilidades_pct']:.1f}%")

if filtrado.empty:
    st.warning("Ninguna oferta coincide con los filtros seleccionados.")
    st.stop()

col_grafico1, col_grafico2 = st.columns(2)
with col_grafico1:
    st.subheader("Habilidades más solicitadas")
    conteo_habilidades = (
        filtrado.explode("habilidades_requeridas")["habilidades_requeridas"]
        .value_counts()
        .drop(labels=["No detallado"], errors="ignore")
        .head(12)
        .sort_values()
        .rename_axis("Habilidad")
        .reset_index(name="Ofertas")
    )
    if conteo_habilidades.empty:
        st.info("No se detectaron habilidades en las ofertas filtradas.")
    else:
        figura_habilidades = px.bar(
            conteo_habilidades,
            x="Ofertas",
            y="Habilidad",
            orientation="h",
            color="Ofertas",
            color_continuous_scale="Teal",
        )
        figura_habilidades.update_layout(coloraxis_showscale=False)
        st.plotly_chart(figura_habilidades, use_container_width=True)

with col_grafico2:
    st.subheader("Nivel de experiencia")
    conteo_experiencia = (
        filtrado["nivel_experiencia"]
        .value_counts()
        .rename_axis("Nivel")
        .reset_index(name="Ofertas")
    )
    figura_experiencia = px.pie(
        conteo_experiencia,
        values="Ofertas",
        names="Nivel",
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Safe,
    )
    st.plotly_chart(figura_experiencia, use_container_width=True)

st.subheader("Ofertas encontradas")
tabla = filtrado[
    [
        "titulo",
        "empresa",
        "ubicacion",
        "nivel_experiencia",
        "habilidades_requeridas",
        "fecha_publicacion",
        "url",
    ]
].copy()
tabla["habilidades_requeridas"] = tabla["habilidades_requeridas"].apply(
    lambda valores: ", ".join(valores)
)
st.dataframe(
    tabla,
    use_container_width=True,
    hide_index=True,
    column_config={
        "titulo": "Puesto",
        "empresa": "Empresa",
        "ubicacion": "Ubicación",
        "nivel_experiencia": "Experiencia",
        "habilidades_requeridas": "Habilidades",
        "fecha_publicacion": "Publicación",
        "url": st.column_config.LinkColumn("Oferta", display_text="Abrir"),
    },
)

st.download_button(
    "Descargar resultados filtrados (CSV)",
    data=_csv_descargable(filtrado),
    file_name="ofertas_computrabajo.csv",
    mime="text/csv",
)

with st.expander("Indicadores de calidad del dataset"):
    st.json(reporte)
