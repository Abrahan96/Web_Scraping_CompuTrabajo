"""Funciones para conectarnos con Computrabajo."""

import re
import unicodedata

import requests


# Los headers permiten que el servidor identifique el tipo de navegador.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-PE,es;q=0.9",
}

URL_BASE = "https://pe.computrabajo.com"


def crear_slug(puesto):
    """Convierte 'Técnico de Farmacia' en 'tecnico-de-farmacia'."""
    texto = puesto.strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(letra for letra in texto if not unicodedata.combining(letra))
    return re.sub(r"[^a-z0-9]+", "-", texto).strip("-")


def construir_url(puesto, pagina=1):
    """Construye la URL que se consultará."""
    slug = crear_slug(puesto)
    return f"{URL_BASE}/trabajo-de-{slug}?p={pagina}"


def conectar(puesto, pagina=1):
    """Realiza la petición HTTP. Devuelve la respuesta o None si falla."""
    url = construir_url(puesto, pagina)
    print(f"Conectando a: {url}")

    try:
        respuesta = requests.get(url, headers=HEADERS, timeout=20)
        respuesta.raise_for_status()

        print(f"Código HTTP: {respuesta.status_code}")
        print(f"Tamaño del HTML: {len(respuesta.text):,} caracteres")
        return respuesta

    except requests.exceptions.Timeout:
        print("ERROR: el servidor tardó demasiado en responder.")
    except requests.exceptions.HTTPError as error:
        print(f"ERROR HTTP: {error}")
    except requests.exceptions.ConnectionError:
        print("ERROR: no se pudo establecer conexión a internet.")

    return None
