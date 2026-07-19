import unittest

from src.limpieza import LimpiadorOfertas


class TestLimpieza(unittest.TestCase):
    def test_limpia_vacios_espacios_y_duplicados(self) -> None:
        ofertas = [
            {"titulo": "  Analista   de Datos ", "empresa": "Empresa A", "ubicacion": "Lima", "url": "url-1"},
            {"titulo": "Analista de Datos", "empresa": "Empresa A", "ubicacion": "Lima", "url": "url-2"},
            {"titulo": "", "empresa": "Empresa B", "ubicacion": "Lima", "url": "url-3"},
            {"titulo": "Practicante", "empresa": "", "ubicacion": "", "url": "url-4"},
        ]
        limpiador = LimpiadorOfertas(ofertas)

        resultado = limpiador.limpiar()

        self.assertEqual(len(resultado), 2)
        self.assertEqual(limpiador.reporte["duplicados_eliminados"], 1)
        self.assertEqual(limpiador.reporte["titulos_vacios_eliminados"], 1)
        self.assertEqual(resultado.loc[1, "empresa"], "Empresa confidencial")
        self.assertEqual(resultado.loc[1, "ubicacion"], "No especificada")


if __name__ == "__main__":
    unittest.main()
