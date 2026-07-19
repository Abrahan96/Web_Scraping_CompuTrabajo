import unittest
from pathlib import Path

from src.exploracion import ExploradorHTML


class TestExploracion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        ruta = Path(__file__).parent / "fixtures" / "listado.html"
        cls.html = ruta.read_text(encoding="utf-8")

    def test_resume_estructura_html(self) -> None:
        resumen = ExploradorHTML(self.html).resumir_estructura()

        self.assertEqual(resumen["tarjetas_detectadas"], 2)
        self.assertGreater(resumen["total_etiquetas"], 0)

    def test_extrae_campos_de_ofertas(self) -> None:
        ofertas = ExploradorHTML(self.html).extraer_ofertas()

        self.assertEqual(len(ofertas), 2)
        self.assertEqual(ofertas[0]["empresa"], "Empresa Uno")
        self.assertEqual(ofertas[1]["ubicacion"], "Arequipa, Arequipa")
        self.assertTrue(ofertas[0]["url"].startswith("https://pe.computrabajo.com/"))


if __name__ == "__main__":
    unittest.main()
