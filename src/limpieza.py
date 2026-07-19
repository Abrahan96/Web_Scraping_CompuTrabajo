"""Limpieza básica y verificable de las ofertas extraídas."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


class LimpiadorOfertas:
    COLUMNAS = ["titulo", "empresa", "ubicacion", "url"]

    def __init__(self, ofertas: list[dict[str, str]]) -> None:
        self.dataframe = pd.DataFrame(ofertas)
        self.reporte: dict[str, Any] = {}

    def limpiar(self) -> pd.DataFrame:
        if self.dataframe.empty:
            raise ValueError("No existen ofertas para limpiar.")
        faltantes = set(self.COLUMNAS) - set(self.dataframe.columns)
        if faltantes:
            raise ValueError(f"Faltan columnas obligatorias: {sorted(faltantes)}")

        df = self.dataframe[self.COLUMNAS].copy()
        for columna in self.COLUMNAS:
            df[columna] = (
                df[columna]
                .fillna("")
                .astype(str)
                .str.replace(r"\s+", " ", regex=True)
                .str.strip()
            )

        filas_entrada = len(df)
        titulos_vacios = int(df["titulo"].eq("").sum())
        df = df[df["titulo"].ne("")].copy()
        df.loc[df["empresa"].eq(""), "empresa"] = "Empresa confidencial"
        df.loc[df["ubicacion"].eq(""), "ubicacion"] = "No especificada"
        antes_duplicados = len(df)
        df.drop_duplicates(subset=["titulo", "empresa", "ubicacion"], inplace=True)

        self.dataframe = df.reset_index(drop=True)
        self.reporte = {
            "filas_entrada": filas_entrada,
            "titulos_vacios_eliminados": titulos_vacios,
            "duplicados_eliminados": antes_duplicados - len(df),
            "filas_salida": len(df),
            "empresas_unicas": int(df["empresa"].nunique()),
        }
        return self.dataframe

    def guardar_csv(self, ruta: str | Path) -> Path:
        if self.dataframe.empty or not self.reporte:
            raise ValueError("Primero debe ejecutarse el proceso de limpieza.")
        destino = Path(ruta)
        destino.parent.mkdir(parents=True, exist_ok=True)
        self.dataframe.to_csv(destino, index=False, encoding="utf-8")
        return destino
