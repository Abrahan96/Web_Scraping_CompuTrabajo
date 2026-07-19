"""Funciones de limpieza básica con Pandas."""

import os

import pandas as pd


def crear_dataframe(ofertas):
    """Convierte la lista de diccionarios en un DataFrame."""
    dataframe = pd.DataFrame(ofertas)
    print(f"Filas antes de limpiar: {len(dataframe)}")
    return dataframe


def limpiar_datos(dataframe):
    """Limpia espacios, vacíos y registros duplicados."""
    df = dataframe.copy()

    # Quitamos espacios adicionales de las columnas de texto.
    columnas = ["titulo", "empresa", "ubicacion", "url"]
    for columna in columnas:
        df[columna] = df[columna].fillna("").astype(str)
        df[columna] = df[columna].str.replace(r"\s+", " ", regex=True).str.strip()

    # Eliminamos registros sin título porque no pueden ser analizados.
    titulos_vacios = (df["titulo"] == "").sum()
    df = df[df["titulo"] != ""].copy()

    # Completamos campos opcionales que no aparecieron en la página.
    df.loc[df["empresa"] == "", "empresa"] = "Empresa confidencial"
    df.loc[df["ubicacion"] == "", "ubicacion"] = "No especificada"

    # Una misma oferta puede repetirse en el HTML.
    filas_antes = len(df)
    df = df.drop_duplicates(subset=["titulo", "empresa", "ubicacion"])
    duplicados = filas_antes - len(df)

    df = df.reset_index(drop=True)

    print("\n--- REPORTE DE LIMPIEZA ---")
    print(f"Títulos vacíos eliminados: {titulos_vacios}")
    print(f"Duplicados eliminados: {duplicados}")
    print(f"Filas después de limpiar: {len(df)}")
    print(f"Empresas diferentes: {df['empresa'].nunique()}")

    return df


def guardar_csv(dataframe, ruta):
    """Guarda el DataFrame limpio en un archivo CSV."""
    carpeta = os.path.dirname(ruta)
    os.makedirs(carpeta, exist_ok=True)
    dataframe.to_csv(ruta, index=False, encoding="utf-8")
    print(f"CSV guardado en: {ruta}")
