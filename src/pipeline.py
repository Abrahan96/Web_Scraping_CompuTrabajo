"""Orquestación explícita del pipeline de ofertas laborales."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from src.ingesta import ExtractorComputrabajo
from src.transformacion import TransformadorDatos


@dataclass(frozen=True)
class ResultadoPipeline:
    datos: pd.DataFrame
    reporte_calidad: dict[str, Any]
    advertencias: tuple[str, ...]


def ejecutar_pipeline(
    palabra_clave: str,
    limite_paginas: int = 2,
    limite_ofertas: int = 40,
) -> ResultadoPipeline:
    extractor = ExtractorComputrabajo(
        palabra_clave=palabra_clave,
        limite_paginas=limite_paginas,
        limite_ofertas=limite_ofertas,
    )
    registros = extractor.ejecutar_extraccion()

    transformador = TransformadorDatos(palabra_clave)
    datos = transformador.ejecutar_pipeline(registros)
    return ResultadoPipeline(
        datos=datos,
        reporte_calidad=transformador.reporte_calidad,
        advertencias=tuple(extractor.advertencias),
    )
