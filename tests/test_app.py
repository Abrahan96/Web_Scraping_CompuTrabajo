import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


class TestAplicacion(unittest.TestCase):
    def test_pantalla_inicial_sin_excepciones(self) -> None:
        ruta = Path(__file__).parents[1] / "app" / "main.py"
        app = AppTest.from_file(str(ruta)).run(timeout=20)

        self.assertEqual(list(app.exception), [])
        self.assertEqual(app.title[0].value, "🔎 Radar Laboral Perú")
        self.assertEqual(app.text_input[0].label, "¿Qué puesto deseas analizar?")
        self.assertEqual(app.button[0].label, "Analizar mercado")


if __name__ == "__main__":
    unittest.main()
