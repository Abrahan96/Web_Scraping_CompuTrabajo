"""Funciones para explorar y extraer información del HTML."""

from urllib.parse import urljoin

from bs4 import BeautifulSoup


URL_BASE = "https://pe.computrabajo.com"


def crear_soup(html):
    """Convierte el texto HTML en un árbol que BeautifulSoup puede recorrer."""
    return BeautifulSoup(html, "html.parser")


def explorar_html(soup):
    """Muestra información general para conocer la estructura de la página."""
    tarjetas = soup.find_all("article", class_="box_offer")
    titulos_h2 = soup.find_all("h2")
    enlaces = soup.find_all("a")
    etiquetas = soup.find_all(True)

    print("\n--- EXPLORACIÓN DEL HTML ---")
    print(f"Título de la página: {soup.title.get_text(strip=True) if soup.title else 'Sin título'}")
    print(f"Total de etiquetas: {len(etiquetas)}")
    print(f"Etiquetas h2: {len(titulos_h2)}")
    print(f"Enlaces: {len(enlaces)}")
    print(f"Tarjetas de empleo: {len(tarjetas)}")

    # Mostramos una tarjeta para entender el contenedor repetible.
    if tarjetas:
        print("\nPrimer título encontrado:")
        primer_titulo = tarjetas[0].find("a", class_="js-o-link")
        print(primer_titulo.get_text(strip=True) if primer_titulo else "No encontrado")

    return len(tarjetas)


def extraer_ofertas(soup):
    """Recorre cada tarjeta y obtiene título, empresa, ubicación y URL."""
    ofertas = []
    tarjetas = soup.find_all("article", class_="box_offer")

    for tarjeta in tarjetas:
        enlace_titulo = tarjeta.find("a", class_="js-o-link")

        # Si la tarjeta no tiene título, no podemos usarla.
        if enlace_titulo is None:
            continue

        titulo = enlace_titulo.get_text(strip=True)
        url = urljoin(URL_BASE, enlace_titulo.get("href", "").split("#")[0])

        bloque_empresa = tarjeta.find("p", class_="dFlex")
        enlace_empresa = bloque_empresa.find("a") if bloque_empresa else None
        empresa = enlace_empresa.get_text(strip=True) if enlace_empresa else "Empresa confidencial"

        ubicacion = "No especificada"
        parrafos = tarjeta.find_all("p", class_="fs16")
        for parrafo in parrafos:
            clases = parrafo.get("class", [])
            if "dFlex" not in clases:
                ubicacion = parrafo.get_text(" ", strip=True)
                break

        ofertas.append(
            {
                "titulo": titulo,
                "empresa": empresa,
                "ubicacion": ubicacion,
                "url": url,
            }
        )

    print(f"\nOfertas extraídas: {len(ofertas)}")
    return ofertas
