"""Conexión HTTP básica con el portal de Computrabajo Perú."""

from __future__ import annotations

import re
import unicodedata
from typing import Any

import requests


class ErrorConexion(RuntimeError):
    """Representa un fallo controlado durante la conexión al portal."""


def crear_slug(texto: str) -> str:
    """Convierte un puesto escrito por el usuario al formato usado en la URL."""
    normalizado = unicodedata.normalize("NFKD", texto.strip().lower())
    sin_tildes = "".join(c for c in normalizado if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", sin_tildes).strip("-")


class ClienteComputrabajo:
    BASE_URL = "https://pe.computrabajo.com"

    def __init__(self, timeout: int = 20, sesion: Any | None = None) -> None:
        self.timeout = timeout
        self.sesion = sesion or requests.Session()
        self.cabeceras = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "es-PE,es;q=0.9",
        }

    @classmethod
    def construir_url(cls, puesto: str, pagina: int = 1) -> str:
        if not puesto.strip():
            raise ValueError("El puesto no puede estar vacío.")
        if pagina < 1:
            raise ValueError("La página debe ser mayor o igual a 1.")
        return f"{cls.BASE_URL}/trabajo-de-{crear_slug(puesto)}?p={pagina}"

    def conectar(self, puesto: str, pagina: int = 1) -> requests.Response:
        """Realiza una solicitud GET y valida el estado y contenido recibido."""
        url = self.construir_url(puesto, pagina)
        try:
            respuesta = self.sesion.get(
                url,
                headers=self.cabeceras,
                timeout=self.timeout,
            )
            respuesta.raise_for_status()
        except requests.RequestException as error:
            raise ErrorConexion(f"No se pudo conectar con {url}: {error}") from error

        if not respuesta.text.strip():
            raise ErrorConexion("La URL respondió correctamente, pero no devolvió contenido HTML.")
        return respuesta
