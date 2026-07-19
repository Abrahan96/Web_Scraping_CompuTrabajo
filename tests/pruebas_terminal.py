"""Pruebas sencillas con assert, sin programación orientada a objetos."""

from pathlib import Path

import pandas as pd

from src.conexion import construir_url, crear_slug
from src.exploracion import crear_soup, explorar_html, extraer_ofertas
from src.limpieza import limpiar_datos


def cargar_html_prueba():
    ruta = Path("tests/fixtures/listado.html")
    return ruta.read_text(encoding="utf-8")


def probar_slug():
    resultado = crear_slug("Técnico de Farmacia")
    assert resultado == "tecnico-de-farmacia"


def probar_url():
    url = construir_url("Analista de Datos", pagina=2)
    assert url.endswith("/trabajo-de-analista-de-datos?p=2")


def probar_exploracion():
    soup = crear_soup(cargar_html_prueba())
    cantidad = explorar_html(soup)
    assert cantidad == 2


def probar_extraccion():
    soup = crear_soup(cargar_html_prueba())
    ofertas = extraer_ofertas(soup)
    assert len(ofertas) == 2
    assert ofertas[0]["empresa"] == "Empresa Uno"
    assert ofertas[1]["ubicacion"] == "Arequipa, Arequipa"


def probar_limpieza():
    datos = [
        {"titulo": "  Analista  ", "empresa": "Empresa A", "ubicacion": "Lima", "url": "url-1"},
        {"titulo": "Analista", "empresa": "Empresa A", "ubicacion": "Lima", "url": "url-2"},
        {"titulo": "", "empresa": "Empresa B", "ubicacion": "Lima", "url": "url-3"},
    ]
    dataframe = pd.DataFrame(datos)
    resultado = limpiar_datos(dataframe)
    assert len(resultado) == 1


def ejecutar_pruebas():
    pruebas = [
        probar_slug,
        probar_url,
        probar_exploracion,
        probar_extraccion,
        probar_limpieza,
    ]

    print("=" * 50)
    print("PRUEBAS DEL PRIMER ENTREGABLE")
    print("=" * 50)

    for prueba in pruebas:
        prueba()
        print(f"OK - {prueba.__name__}")

    print(f"\nResultado: {len(pruebas)} pruebas correctas.")


if __name__ == "__main__":
    ejecutar_pruebas()
