"""Ingesta de ofertas públicas de Computrabajo Perú.

La página de listado se usa para descubrir ofertas y el detalle estructurado
``JobPosting`` se usa como fuente principal de los atributos de cada empleo.
"""

from __future__ import annotations

import json
import logging
import random
import re
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urljoin

import cloudscraper
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


LOGGER = logging.getLogger(__name__)
BASE_URL = "https://pe.computrabajo.com"


class ErrorIngesta(RuntimeError):
    """Error controlado durante la consulta o interpretación de la fuente."""


class SinOfertasError(ErrorIngesta):
    """La búsqueda terminó correctamente, pero no produjo ofertas utilizables."""


def _texto_limpio(valor: Any) -> str:
    if valor is None:
        return ""
    texto = BeautifulSoup(str(valor), "html.parser").get_text("\n")
    texto = texto.replace("\xa0", " ")
    lineas = [re.sub(r"\s+", " ", linea).strip() for linea in texto.splitlines()]
    return "\n".join(linea for linea in lineas if linea)


def _slug_busqueda(texto: str) -> str:
    normalizado = unicodedata.normalize("NFKD", texto.strip().lower())
    sin_tildes = "".join(c for c in normalizado if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", sin_tildes).strip("-")


def normalizar_etiqueta(texto: str) -> str:
    """Normaliza rótulos HTML para comparaciones internas tolerantes a tildes."""
    normalizado = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in normalizado if not unicodedata.combining(c)).strip()


class ExtractorComputrabajo:
    """Extrae listados y detalles de ofertas con límites configurables."""

    def __init__(
        self,
        palabra_clave: str,
        limite_paginas: int = 2,
        limite_ofertas: int = 40,
        timeout: int = 20,
        pausa_minima: float = 0.4,
        pausa_maxima: float = 0.9,
        cliente_web: Any | None = None,
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> None:
        if not palabra_clave or not palabra_clave.strip():
            raise ValueError("La palabra clave no puede estar vacía.")
        if not 1 <= limite_paginas <= 10:
            raise ValueError("El límite de páginas debe estar entre 1 y 10.")
        if not 1 <= limite_ofertas <= 200:
            raise ValueError("El límite de ofertas debe estar entre 1 y 200.")

        self.palabra_clave_original = palabra_clave.strip()
        self.palabra_clave = _slug_busqueda(palabra_clave)
        self.limite_paginas = limite_paginas
        self.limite_ofertas = limite_ofertas
        self.timeout = timeout
        self.pausa_minima = pausa_minima
        self.pausa_maxima = pausa_maxima
        self.sleep_fn = sleep_fn
        self.url_base = f"{BASE_URL}/trabajo-de-{self.palabra_clave}"
        self.datos_empleos: list[dict[str, Any]] = []
        self.advertencias: list[str] = []

        self.cliente_web = cliente_web or self._crear_cliente()
        self.cabeceras = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "es-PE,es;q=0.9",
        }

    @staticmethod
    def _crear_cliente() -> Any:
        cliente = cloudscraper.create_scraper()
        reintentos = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=0.8,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET"}),
            respect_retry_after_header=True,
        )
        adaptador = HTTPAdapter(max_retries=reintentos)
        cliente.mount("https://", adaptador)
        return cliente

    def _descargar(self, url: str) -> str:
        try:
            respuesta = self.cliente_web.get(
                url,
                headers=self.cabeceras,
                timeout=self.timeout,
            )
            respuesta.raise_for_status()
        except Exception as error:
            raise ErrorIngesta(f"No se pudo consultar {url}: {error}") from error

        contenido = respuesta.text
        if not contenido.strip() or "Just a moment" in contenido:
            raise ErrorIngesta("La fuente devolvió una respuesta vacía o de verificación.")
        return contenido

    def descargar_pagina(self, numero_pagina: int) -> str:
        return self._descargar(f"{self.url_base}?p={numero_pagina}")

    @staticmethod
    def _empresa_desde_tarjeta(tarjeta: Any) -> str:
        enlace = tarjeta.select_one("p.dFlex.fs16 a, p.fs16 a.t_ellipsis")
        if enlace:
            return _texto_limpio(enlace.get_text(" ", strip=True))

        bloque = tarjeta.select_one("p.dFlex.fs16, p.fs16")
        if not bloque:
            return "Empresa confidencial"
        texto = _texto_limpio(bloque.get_text(" ", strip=True))
        return re.sub(r"^\d+[,.]\d+\s*", "", texto) or "Empresa confidencial"

    @staticmethod
    def _ubicacion_desde_tarjeta(tarjeta: Any) -> str:
        for bloque in tarjeta.select("p.fs16.fc_base.mt5"):
            if "dFlex" not in (bloque.get("class") or []):
                return _texto_limpio(bloque.get_text(" ", strip=True))
        return ""

    def extraer_datos_ofertas(self, codigo_html: str) -> list[dict[str, Any]]:
        """Interpreta tarjetas y devuelve las ofertas nuevas descubiertas."""
        arbol_html = BeautifulSoup(codigo_html, "html.parser")
        tarjetas = arbol_html.select("article.box_offer")
        descubiertas: list[dict[str, Any]] = []
        urls_existentes = {empleo.get("url") for empleo in self.datos_empleos}

        for tarjeta in tarjetas:
            enlace = tarjeta.select_one("a.js-o-link[href], h2 a[href]")
            if not enlace:
                continue
            url = urljoin(BASE_URL, enlace.get("href", "").split("#")[0])
            if not url or url in urls_existentes:
                continue

            registro = {
                "id_oferta": tarjeta.get("id", ""),
                "titulo": _texto_limpio(enlace.get_text(" ", strip=True)),
                "empresa": self._empresa_desde_tarjeta(tarjeta),
                "ubicacion": self._ubicacion_desde_tarjeta(tarjeta),
                "fecha_publicacion": "",
                "fecha_relativa": _texto_limpio(
                    tarjeta.select_one("p.fs13.fc_aux.mt15").get_text(" ", strip=True)
                )
                if tarjeta.select_one("p.fs13.fc_aux.mt15")
                else "",
                "tipo_contrato": "",
                "salario": "",
                "descripcion": "",
                "url": url,
                "detalle_disponible": False,
                "fuente": "Computrabajo Perú",
                "termino_busqueda": self.palabra_clave_original,
            }
            descubiertas.append(registro)
            urls_existentes.add(url)

        self.datos_empleos.extend(descubiertas)
        return descubiertas

    @staticmethod
    def _encontrar_job_posting(arbol_html: BeautifulSoup) -> dict[str, Any] | None:
        for script in arbol_html.find_all("script", attrs={"type": "application/ld+json"}):
            try:
                contenido = json.loads(script.string or script.get_text())
            except (json.JSONDecodeError, TypeError):
                continue

            candidatos: list[Any]
            if isinstance(contenido, dict) and isinstance(contenido.get("@graph"), list):
                candidatos = contenido["@graph"]
            elif isinstance(contenido, list):
                candidatos = contenido
            else:
                candidatos = [contenido]

            for candidato in candidatos:
                if isinstance(candidato, dict) and candidato.get("@type") == "JobPosting":
                    return candidato
        return None

    @staticmethod
    def _formatear_salario(salario: Any) -> str:
        if not isinstance(salario, dict):
            return ""
        moneda = salario.get("currency", "")
        valor = salario.get("value", {})
        if isinstance(valor, dict):
            cantidad = valor.get("value") or valor.get("minValue")
            maximo = valor.get("maxValue")
            unidad = valor.get("unitText", "")
        else:
            cantidad, maximo, unidad = valor, None, ""
        if not cantidad:
            return ""
        rango = f"{cantidad:g}" if isinstance(cantidad, (int, float)) else str(cantidad)
        if maximo and maximo != cantidad:
            rango += f" - {maximo:g}" if isinstance(maximo, (int, float)) else f" - {maximo}"
        return " ".join(parte for parte in (moneda, rango, unidad) if parte)

    @staticmethod
    def _ubicacion_desde_esquema(job: dict[str, Any]) -> str:
        ubicacion = job.get("jobLocation", {})
        if isinstance(ubicacion, list):
            ubicacion = ubicacion[0] if ubicacion else {}
        direccion = ubicacion.get("address", {}) if isinstance(ubicacion, dict) else {}
        if isinstance(direccion, str):
            return direccion
        partes = [
            direccion.get("addressRegion", ""),
            direccion.get("addressLocality", ""),
            direccion.get("addressCountry", ""),
        ]
        return ", ".join(dict.fromkeys(parte for parte in partes if parte))

    @staticmethod
    def _extraer_detalle_html(
        arbol_html: BeautifulSoup,
        registro: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Respaldo para ofertas que muestran detalle pero omiten JobPosting."""
        seccion = None
        for encabezado in arbol_html.select("main h3"):
            if "descripcion de la oferta" in normalizar_etiqueta(encabezado.get_text(" ")):
                seccion = encabezado.parent
                break
        if seccion is None:
            return None

        parrafo = seccion.select_one("p.mbB")
        requerimientos = seccion.select_one("ul.disc")
        palabras_clave = seccion.select_one("p.fc_aux.fs13.mbB")
        partes_descripcion = [
            elemento.get_text("\n", strip=True)
            for elemento in (parrafo, requerimientos, palabras_clave)
            if elemento
        ]
        descripcion = _texto_limpio("\n".join(partes_descripcion))
        if not descripcion:
            return None

        etiquetas = [
            _texto_limpio(etiqueta.get_text(" ", strip=True))
            for etiqueta in seccion.select("div.mbB span.tag")
        ]
        salario = next(
            (
                valor
                for valor in etiquetas
                if re.search(r"(?:s/\.|pen|usd|\$)\s*\d", valor, flags=re.IGNORECASE)
            ),
            "",
        )
        tipos = [
            valor
            for valor in etiquetas
            if valor and valor != salario and valor.lower() != "a convenir"
        ]
        fecha = seccion.select_one("p.fc_aux.fs13:not(.mbB)")

        registro.update(
            {
                "descripcion": descripcion,
                "tipo_contrato": " | ".join(tipos),
                "salario": salario,
                "fecha_relativa": _texto_limpio(fecha.get_text(" ", strip=True))
                if fecha
                else registro.get("fecha_relativa", ""),
                "detalle_disponible": True,
            }
        )
        return registro

    def extraer_detalle_oferta(self, registro: dict[str, Any]) -> dict[str, Any]:
        arbol_html = BeautifulSoup(self._descargar(registro["url"]), "html.parser")
        job = self._encontrar_job_posting(arbol_html)
        if not job:
            respaldo = self._extraer_detalle_html(arbol_html, registro)
            if respaldo:
                return respaldo
            raise ErrorIngesta("La oferta no contiene un detalle interpretable.")

        organizacion = job.get("hiringOrganization", {})
        identificador = job.get("identifier", {})
        registro.update(
            {
                "id_oferta": identificador.get("value", registro["id_oferta"])
                if isinstance(identificador, dict)
                else registro["id_oferta"],
                "titulo": _texto_limpio(job.get("title")) or registro["titulo"],
                "empresa": _texto_limpio(organizacion.get("name"))
                if isinstance(organizacion, dict) and organizacion.get("name")
                else registro["empresa"],
                "ubicacion": self._ubicacion_desde_esquema(job) or registro["ubicacion"],
                "fecha_publicacion": _texto_limpio(job.get("datePosted")),
                "tipo_contrato": _texto_limpio(job.get("employmentType")),
                "salario": self._formatear_salario(job.get("baseSalary")),
                "descripcion": _texto_limpio(job.get("description")),
                "url": job.get("url") or registro["url"],
                "detalle_disponible": True,
            }
        )
        return registro

    def _pausar(self) -> None:
        if self.pausa_maxima > 0:
            self.sleep_fn(random.uniform(self.pausa_minima, self.pausa_maxima))

    def guardar_en_crudo_json(self, ruta: str | Path = "data/raw/ultima_busqueda.json") -> Path:
        destino = Path(ruta)
        destino.parent.mkdir(parents=True, exist_ok=True)
        temporal = destino.with_suffix(destino.suffix + ".tmp")
        temporal.write_text(
            json.dumps(self.datos_empleos, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporal.replace(destino)
        return destino

    def ejecutar_extraccion(
        self,
        ruta_salida: str | Path = "data/raw/ultima_busqueda.json",
    ) -> list[dict[str, Any]]:
        """Ejecuta listado + detalle y persiste una copia cruda atómica."""
        self.datos_empleos = []
        self.advertencias = []

        for pagina in range(1, self.limite_paginas + 1):
            html = self.descargar_pagina(pagina)
            nuevas = self.extraer_datos_ofertas(html)
            LOGGER.info("Página %s: %s ofertas nuevas", pagina, len(nuevas))
            if len(self.datos_empleos) >= self.limite_ofertas:
                break
            if pagina < self.limite_paginas:
                self._pausar()

        self.datos_empleos = self.datos_empleos[: self.limite_ofertas]
        if not self.datos_empleos:
            raise SinOfertasError(
                f"No se encontraron ofertas para '{self.palabra_clave_original}'."
            )

        for indice, registro in enumerate(self.datos_empleos):
            try:
                self.extraer_detalle_oferta(registro)
            except ErrorIngesta as error:
                mensaje = f"No se pudo obtener el detalle de '{registro['titulo']}': {error}"
                self.advertencias.append(mensaje)
                LOGGER.warning(mensaje)
            if indice < len(self.datos_empleos) - 1:
                self._pausar()

        instante = datetime.now(timezone.utc).isoformat()
        for registro in self.datos_empleos:
            registro["fecha_extraccion_utc"] = instante

        self.guardar_en_crudo_json(ruta_salida)
        return self.datos_empleos


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    extractor = ExtractorComputrabajo("analista de datos", limite_paginas=1, limite_ofertas=10)
    extractor.ejecutar_extraccion()
