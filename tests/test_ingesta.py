import json
import unittest

from src.ingesta import ExtractorComputrabajo


class RespuestaFalsa:
    def __init__(self, texto: str):
        self.text = texto

    def raise_for_status(self) -> None:
        return None


class ClienteFalso:
    def __init__(self, respuestas: dict[str, str]):
        self.respuestas = respuestas

    def get(self, url: str, **_: object) -> RespuestaFalsa:
        return RespuestaFalsa(self.respuestas[url])


class TestIngesta(unittest.TestCase):
    def test_extrae_tarjeta_sin_depender_de_la_red(self) -> None:
        html = """
        <article class="box_offer" id="ABC123">
          <h2><a class="js-o-link" href="/ofertas-de-trabajo/oferta-prueba#lista">Analista SQL</a></h2>
          <p class="dFlex fs16 fc_base mt5"><span>4,5</span><a class="fc_base t_ellipsis">Empresa Uno</a></p>
          <p class="fs16 fc_base mt5"><span>Lima, Lima</span></p>
          <p class="fs13 fc_aux mt15">Hace 2 horas</p>
        </article>
        """
        extractor = ExtractorComputrabajo(
            "analista de datos", cliente_web=ClienteFalso({}), pausa_maxima=0
        )

        registros = extractor.extraer_datos_ofertas(html)

        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0]["empresa"], "Empresa Uno")
        self.assertEqual(registros[0]["ubicacion"], "Lima, Lima")
        self.assertTrue(registros[0]["url"].endswith("/ofertas-de-trabajo/oferta-prueba"))

    def test_prioriza_job_posting_para_el_detalle(self) -> None:
        url = "https://pe.computrabajo.com/ofertas-de-trabajo/oferta-prueba"
        job = {
            "@graph": [
                {"@type": "Organization", "name": "Computrabajo"},
                {
                    "@type": "JobPosting",
                    "title": "Analista de Datos Senior",
                    "description": "Requisitos: SQL, Python e inglés avanzado.",
                    "datePosted": "2026-07-19",
                    "employmentType": "FULL_TIME",
                    "url": url,
                    "hiringOrganization": {"name": "Empresa Dos"},
                    "identifier": {"value": "OFERTA-2"},
                    "jobLocation": {
                        "address": {
                            "addressRegion": "Miraflores",
                            "addressLocality": "Lima",
                            "addressCountry": "Perú",
                        }
                    },
                    "baseSalary": {
                        "currency": "PEN",
                        "value": {"value": 3000, "unitText": "MONTH"},
                    },
                },
            ]
        }
        html = f'<script type="application/ld+json">{json.dumps(job)}</script>'
        extractor = ExtractorComputrabajo(
            "datos", cliente_web=ClienteFalso({url: html}), pausa_maxima=0
        )
        registro = {
            "id_oferta": "",
            "titulo": "Título listado",
            "empresa": "Empresa",
            "ubicacion": "",
            "url": url,
        }

        detalle = extractor.extraer_detalle_oferta(registro)

        self.assertTrue(detalle["detalle_disponible"])
        self.assertEqual(detalle["empresa"], "Empresa Dos")
        self.assertIn("SQL", detalle["descripcion"])
        self.assertEqual(detalle["salario"], "PEN 3000 MONTH")

    def test_usa_respaldo_html_si_no_hay_job_posting(self) -> None:
        url = "https://pe.computrabajo.com/ofertas-de-trabajo/oferta-html"
        html = """
        <main>
          <div class="box_detail fl">
            <div class="mb40 pb40 bb1">
              <h3>Descripción de la oferta</h3>
              <div class="mbB">
                <span class="tag">A convenir</span>
                <span class="tag">Contrato indefinido</span>
                <span class="tag">Tiempo completo</span>
              </div>
              <p class="mbB">Requisitos: Excel, atención al cliente e inglés.</p>
              <p class="fwB">Requerimientos</p>
              <ul class="disc"><li>1 año de experiencia</li></ul>
              <p class="fc_aux fs13 mbB">Palabras clave: excel</p>
              <p class="fc_aux fs13">Hace 2 horas</p>
            </div>
          </div>
        </main>
        """
        extractor = ExtractorComputrabajo(
            "datos", cliente_web=ClienteFalso({url: html}), pausa_maxima=0
        )
        registro = {"titulo": "Analista", "url": url, "fecha_relativa": ""}

        detalle = extractor.extraer_detalle_oferta(registro)

        self.assertTrue(detalle["detalle_disponible"])
        self.assertIn("atención al cliente", detalle["descripcion"])
        self.assertEqual(detalle["tipo_contrato"], "Contrato indefinido | Tiempo completo")
        self.assertEqual(detalle["salario"], "")


if __name__ == "__main__":
    unittest.main()
