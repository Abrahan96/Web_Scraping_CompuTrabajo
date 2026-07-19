"""Ejecución por terminal del primer avance académico."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.conexion import ClienteComputrabajo, ErrorConexion
from src.exploracion import ExploradorHTML
from src.limpieza import LimpiadorOfertas


RUTA_CRUDA = Path("data/raw/ultima_extraccion.json")
RUTA_LIMPIA = Path("data/processed/ofertas_limpias.csv")


def ejecutar(puesto: str, paginas: int) -> int:
    cliente = ClienteComputrabajo()
    ofertas: list[dict[str, str]] = []

    print(f"[1/4] Conectando con Computrabajo para: {puesto}")
    for pagina in range(1, paginas + 1):
        respuesta = cliente.conectar(puesto, pagina)
        print(f"  Página {pagina}: HTTP {respuesta.status_code} - {len(respuesta.text):,} caracteres")

        explorador = ExploradorHTML(respuesta.text)
        resumen = explorador.resumir_estructura()
        print("[2/4] Exploración de la estructura HTML")
        print(json.dumps(resumen, ensure_ascii=False, indent=2))

        extraidas = explorador.extraer_ofertas()
        print(f"  Ofertas extraídas en la página: {len(extraidas)}")
        ofertas.extend(extraidas)

    RUTA_CRUDA.parent.mkdir(parents=True, exist_ok=True)
    RUTA_CRUDA.write_text(json.dumps(ofertas, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[3/4] Datos crudos guardados en {RUTA_CRUDA}")

    limpiador = LimpiadorOfertas(ofertas)
    dataframe = limpiador.limpiar()
    limpiador.guardar_csv(RUTA_LIMPIA)
    print("[4/4] Limpieza completada")
    print(json.dumps(limpiador.reporte, ensure_ascii=False, indent=2))
    print(dataframe.head(10).to_string(index=False))
    print(f"CSV limpio guardado en {RUTA_LIMPIA}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Primer avance del analizador laboral")
    parser.add_argument("--puesto", default="analista de datos", help="Puesto a consultar")
    parser.add_argument("--paginas", type=int, default=1, choices=range(1, 4))
    argumentos = parser.parse_args()
    try:
        return ejecutar(argumentos.puesto, argumentos.paginas)
    except (ErrorConexion, ValueError) as error:
        print(f"ERROR: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
