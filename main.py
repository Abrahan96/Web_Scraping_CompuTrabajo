"""Primer entregable: conexión, exploración y limpieza desde terminal."""

import json
import os

from src.conexion import conectar
from src.exploracion import crear_soup, explorar_html, extraer_ofertas
from src.limpieza import crear_dataframe, guardar_csv, limpiar_datos


# Si el usuario no escribe un puesto, usamos este valor de ejemplo.
PUESTO_POR_DEFECTO = "analista de datos"
CANTIDAD_PAGINAS = 1


def guardar_json(ofertas, ruta):
    """Guarda la información sin limpiar para conservar la fuente original."""
    carpeta = os.path.dirname(ruta)
    os.makedirs(carpeta, exist_ok=True)

    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(ofertas, archivo, ensure_ascii=False, indent=2)

    print(f"JSON guardado en: {ruta}")


def solicitar_puesto():
    """Solicita el puesto al usuario mediante la terminal."""
    puesto = input(
        f"Escribe el puesto que deseas buscar [{PUESTO_POR_DEFECTO}]: "
    ).strip()

    # Si solo presiona Enter, usamos el ejemplo predeterminado.
    if puesto == "":
        puesto = PUESTO_POR_DEFECTO

    return puesto


def ejecutar_scraping():
    """Ejecuta paso a paso el primer avance del proyecto."""
    todas_las_ofertas = []
    puesto_buscado = solicitar_puesto()

    print("=" * 60)
    print("ANALIZADOR DE OFERTAS DE COMPUTRABAJO")
    print("=" * 60)
    print(f"Puesto buscado: {puesto_buscado}")

    for pagina in range(1, CANTIDAD_PAGINAS + 1):
        print(f"\nProcesando página {pagina}...")
        respuesta = conectar(puesto_buscado, pagina)

        if respuesta is None:
            print("No se pudo procesar esta página.")
            continue

        soup = crear_soup(respuesta.text)
        explorar_html(soup)
        ofertas_pagina = extraer_ofertas(soup)
        todas_las_ofertas.extend(ofertas_pagina)

    if len(todas_las_ofertas) == 0:
        print("No se encontraron ofertas. El proceso ha terminado.")
        return

    guardar_json(todas_las_ofertas, "data/raw/ultima_extraccion.json")

    dataframe = crear_dataframe(todas_las_ofertas)
    dataframe_limpio = limpiar_datos(dataframe)

    print("\n--- PRIMERAS OFERTAS LIMPIAS ---")
    print(dataframe_limpio.head(10).to_string(index=False))

    guardar_csv(dataframe_limpio, "data/processed/ofertas_limpias.csv")
    print("\nProceso finalizado correctamente.")


if __name__ == "__main__":
    ejecutar_scraping()
