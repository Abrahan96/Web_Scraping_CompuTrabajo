"""Limpieza, validación y enriquecimiento de ofertas laborales."""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


class ErrorCalidadDatos(ValueError):
    """El dataset no cumple las condiciones mínimas para ser analizado."""


def normalizar_texto(valor: Any) -> str:
    texto = "" if valor is None else str(valor)
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texto).strip()


class TransformadorDatos:
    COLUMNAS_TEXTO = [
        "id_oferta",
        "titulo",
        "empresa",
        "ubicacion",
        "fecha_publicacion",
        "fecha_relativa",
        "tipo_contrato",
        "salario",
        "descripcion",
        "url",
        "fuente",
        "termino_busqueda",
        "fecha_extraccion_utc",
    ]

    def __init__(
        self,
        palabra_clave: str,
        ruta_taxonomia: str | Path = "config/habilidades.csv",
    ) -> None:
        self.palabra_clave = palabra_clave.strip()
        self.ruta_entrada = Path("data/raw/ultima_busqueda.json")
        self.ruta_salida_csv = Path("data/processed/ultima_busqueda.csv")
        self.ruta_salida_parquet = Path("data/processed/ultima_busqueda.parquet")
        self.ruta_reporte = Path("data/processed/reporte_calidad.json")
        self.ruta_taxonomia = Path(ruta_taxonomia)
        self.dataframe: pd.DataFrame | None = None
        self.reporte_calidad: dict[str, Any] = {}
        self._duplicados_eliminados = 0

    def cargar_datos(
        self,
        registros: Iterable[dict[str, Any]] | None = None,
        ruta: str | Path | None = None,
    ) -> pd.DataFrame:
        if registros is not None:
            self.dataframe = pd.DataFrame(list(registros))
        else:
            origen = Path(ruta) if ruta else self.ruta_entrada
            if not origen.exists():
                raise ErrorCalidadDatos(f"No existe el archivo de entrada: {origen}")
            self.dataframe = pd.read_json(origen)
        return self.dataframe

    def _cargar_taxonomia(self) -> list[tuple[str, str, list[str]]]:
        if not self.ruta_taxonomia.exists():
            raise ErrorCalidadDatos(f"No existe la taxonomía: {self.ruta_taxonomia}")
        taxonomia = pd.read_csv(self.ruta_taxonomia)
        requeridas = {"habilidad", "categoria", "sinonimos"}
        if not requeridas.issubset(taxonomia.columns):
            raise ErrorCalidadDatos("La taxonomía de habilidades tiene un esquema inválido.")

        resultado = []
        for fila in taxonomia.itertuples(index=False):
            sinonimos = [
                normalizar_texto(valor)
                for valor in str(fila.sinonimos).split("|")
                if normalizar_texto(valor)
            ]
            resultado.append((str(fila.habilidad), str(fila.categoria), sinonimos))
        return resultado

    @staticmethod
    def _contiene(texto: str, expresion: str) -> bool:
        patron = rf"(?<!\w){re.escape(expresion)}(?!\w)"
        return bool(re.search(patron, texto))

    def _extraer_habilidades(
        self,
        texto: str,
        taxonomia: list[tuple[str, str, list[str]]],
    ) -> list[str]:
        normalizado = normalizar_texto(texto)
        encontradas = [
            habilidad
            for habilidad, _, sinonimos in taxonomia
            if any(self._contiene(normalizado, sinonimo) for sinonimo in sinonimos)
        ]
        return encontradas or ["No detallado"]

    @staticmethod
    def _clasificar_experiencia(titulo: str, descripcion: str) -> str:
        titulo_n = normalizar_texto(titulo)
        descripcion_n = normalizar_texto(descripcion)
        patrones = [
            ("Liderazgo / Senior", r"\b(sr|senior|jefe|gerente|director|lider|supervisor)\b"),
            ("Entrada / Junior", r"\b(jr|junior|practicante|trainee|asistente|sin experiencia)\b"),
            ("Mandos medios", r"\b(semi senior|semisenior|analista|especialista|coordinador|ejecutivo)\b"),
        ]
        for nivel, patron in patrones:
            if re.search(patron, titulo_n):
                return nivel

        anios = [
            int(valor)
            for valor in re.findall(r"(?:experiencia[^.\n]{0,40}?|minimo\s+)(\d+)\s+anos?", descripcion_n)
        ]
        if anios:
            minimo = max(anios)
            if minimo >= 5:
                return "Liderazgo / Senior"
            if minimo >= 2:
                return "Mandos medios"
            return "Entrada / Junior"
        return "No especificado"

    @staticmethod
    def _ubicacion_partes(ubicacion: str) -> tuple[str, str]:
        partes = [parte.strip() for parte in str(ubicacion).split(",") if parte.strip()]
        departamento = partes[-2] if len(partes) >= 3 else (partes[-1] if partes else "")
        distrito = partes[0] if len(partes) >= 2 else ""
        return distrito, departamento

    def aplicar_limpieza_y_reglas(self) -> pd.DataFrame:
        if self.dataframe is None or self.dataframe.empty:
            raise ErrorCalidadDatos("No hay ofertas para transformar.")
        if not {"titulo", "empresa"}.issubset(self.dataframe.columns):
            raise ErrorCalidadDatos("Faltan las columnas obligatorias: titulo y empresa.")

        df = self.dataframe.copy()
        for columna in self.COLUMNAS_TEXTO:
            if columna not in df.columns:
                df[columna] = ""
            df[columna] = df[columna].fillna("").astype(str).str.replace(r"\s+", " ", regex=True).str.strip()

        if "detalle_disponible" not in df.columns:
            df["detalle_disponible"] = False
        df["detalle_disponible"] = df["detalle_disponible"].fillna(False).astype(bool)

        df = df[df["titulo"].ne("")].copy()
        antes = len(df)
        claves = ["url"] if df["url"].ne("").all() else ["titulo", "empresa", "ubicacion"]
        df.drop_duplicates(subset=claves, keep="first", inplace=True)
        self._duplicados_eliminados = antes - len(df)
        if df.empty:
            raise ErrorCalidadDatos("Todas las filas fueron descartadas durante la validación.")

        taxonomia = self._cargar_taxonomia()
        texto_analisis = (df["titulo"] + " " + df["descripcion"]).str.strip()
        df["habilidades_requeridas"] = texto_analisis.apply(
            lambda texto: self._extraer_habilidades(texto, taxonomia)
        )
        df["nivel_experiencia"] = [
            self._clasificar_experiencia(titulo, descripcion)
            for titulo, descripcion in zip(df["titulo"], df["descripcion"], strict=True)
        ]
        ubicaciones = df["ubicacion"].apply(self._ubicacion_partes)
        df["distrito"] = ubicaciones.str[0]
        df["departamento"] = ubicaciones.str[1]
        df["cantidad_habilidades"] = df["habilidades_requeridas"].apply(
            lambda valores: 0 if valores == ["No detallado"] else len(valores)
        )

        self.dataframe = df.reset_index(drop=True)
        self._generar_reporte_calidad()
        return self.dataframe

    def _generar_reporte_calidad(self) -> dict[str, Any]:
        assert self.dataframe is not None
        df = self.dataframe
        self.reporte_calidad = {
            "total_registros": int(len(df)),
            "duplicados_eliminados": int(self._duplicados_eliminados),
            "cobertura_detalle_pct": round(float(df["detalle_disponible"].mean() * 100), 2),
            "cobertura_habilidades_pct": round(float(df["cantidad_habilidades"].gt(0).mean() * 100), 2),
            "cobertura_experiencia_pct": round(
                float(df["nivel_experiencia"].ne("No especificado").mean() * 100), 2
            ),
            "empresas_unicas": int(df["empresa"].nunique()),
            "campos_vacios": {
                columna: int(df[columna].eq("").sum())
                for columna in ("titulo", "empresa", "ubicacion", "descripcion", "url")
            },
        }
        return self.reporte_calidad

    @staticmethod
    def _escritura_atomica_texto(destino: Path, contenido: str) -> None:
        destino.parent.mkdir(parents=True, exist_ok=True)
        temporal = destino.with_suffix(destino.suffix + ".tmp")
        temporal.write_text(contenido, encoding="utf-8")
        temporal.replace(destino)

    def exportar_datos_procesados(self) -> tuple[Path, Path]:
        if self.dataframe is None or self.dataframe.empty:
            raise ErrorCalidadDatos("No hay datos procesados para exportar.")
        self.ruta_salida_parquet.parent.mkdir(parents=True, exist_ok=True)

        temporal_parquet = self.ruta_salida_parquet.with_suffix(".parquet.tmp")
        self.dataframe.to_parquet(temporal_parquet, index=False)
        temporal_parquet.replace(self.ruta_salida_parquet)

        csv_df = self.dataframe.copy()
        csv_df["habilidades_requeridas"] = csv_df["habilidades_requeridas"].apply(
            lambda valores: " | ".join(valores)
        )
        self._escritura_atomica_texto(
            self.ruta_salida_csv,
            csv_df.to_csv(index=False, lineterminator="\n"),
        )
        self._escritura_atomica_texto(
            self.ruta_reporte,
            json.dumps(self.reporte_calidad, ensure_ascii=False, indent=2),
        )
        return self.ruta_salida_csv, self.ruta_salida_parquet

    def ejecutar_pipeline(
        self,
        registros: Iterable[dict[str, Any]] | None = None,
    ) -> pd.DataFrame:
        self.cargar_datos(registros=registros)
        self.aplicar_limpieza_y_reglas()
        self.exportar_datos_procesados()
        assert self.dataframe is not None
        return self.dataframe


if __name__ == "__main__":
    transformador = TransformadorDatos("analista de datos")
    transformador.ejecutar_pipeline()
