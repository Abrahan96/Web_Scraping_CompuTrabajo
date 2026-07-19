"""Exploración reproducible del HTML y extracción inicial de tarjetas."""

from __future__ import annotations

from collections import Counter
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup


BASE_URL = "https://pe.computrabajo.com"


def _texto(elemento: Any) -> str:
    return elemento.get_text(" ", strip=True) if elemento else ""


class ExploradorHTML:
    def __init__(self, codigo_html: str) -> None:
        if not codigo_html.strip():
            raise ValueError("No se puede explorar un documento HTML vacío.")
        self.sopa = BeautifulSoup(codigo_html, "html.parser")

    def resumir_estructura(self) -> dict[str, Any]:
        """Devuelve métricas útiles para estudiar la estructura en terminal."""
        etiquetas = Counter(elemento.name for elemento in self.sopa.find_all(True))
        clases = Counter(
            clase
            for elemento in self.sopa.find_all(True)
            for clase in (elemento.get("class") or [])
        )
        return {
            "titulo_pagina": _texto(self.sopa.title),
            "total_etiquetas": sum(etiquetas.values()),
            "tarjetas_detectadas": len(self.sopa.select("article.box_offer")),
            "etiquetas_frecuentes": dict(etiquetas.most_common(8)),
            "clases_frecuentes": dict(clases.most_common(8)),
        }

    @staticmethod
    def _extraer_empresa(tarjeta: Any) -> str:
        empresa = tarjeta.select_one("p.dFlex.fs16 a, p.fs16 a.t_ellipsis")
        return _texto(empresa) or "Empresa confidencial"

    @staticmethod
    def _extraer_ubicacion(tarjeta: Any) -> str:
        for bloque in tarjeta.select("p.fs16.fc_base.mt5"):
            if "dFlex" not in (bloque.get("class") or []):
                return _texto(bloque)
        return "No especificada"

    def extraer_ofertas(self) -> list[dict[str, str]]:
        ofertas: list[dict[str, str]] = []
        for tarjeta in self.sopa.select("article.box_offer"):
            enlace = tarjeta.select_one("a.js-o-link[href], h2 a[href]")
            if not enlace:
                continue
            ofertas.append(
                {
                    "titulo": _texto(enlace),
                    "empresa": self._extraer_empresa(tarjeta),
                    "ubicacion": self._extraer_ubicacion(tarjeta),
                    "url": urljoin(BASE_URL, enlace.get("href", "").split("#")[0]),
                }
            )
        return ofertas
