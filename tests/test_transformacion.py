import tempfile
import unittest
from pathlib import Path

from src.transformacion import TransformadorDatos


class TestTransformacion(unittest.TestCase):
    def setUp(self) -> None:
        self.registros = [
            {
                "titulo": "Analista Senior de Datos",
                "empresa": "Empresa A",
                "ubicacion": "San Isidro, Lima, Perú",
                "descripcion": "Requisitos: SQL, Python, Power BI e inglés. Comunicación efectiva.",
                "url": "https://example.test/1",
                "detalle_disponible": True,
            },
            {
                "titulo": "Practicante de marketing",
                "empresa": "Empresa B",
                "ubicacion": "Arequipa, Arequipa, Perú",
                "descripcion": "Conocimientos de SEO y trabajo en equipo.",
                "url": "https://example.test/2",
                "detalle_disponible": True,
            },
        ]

    def test_detecta_tildes_habilidades_y_precedencia(self) -> None:
        transformador = TransformadorDatos("datos")
        transformador.cargar_datos(self.registros)

        df = transformador.aplicar_limpieza_y_reglas()

        self.assertEqual(df.loc[0, "nivel_experiencia"], "Liderazgo / Senior")
        self.assertIn("Inglés", df.loc[0, "habilidades_requeridas"])
        self.assertIn("Comunicación", df.loc[0, "habilidades_requeridas"])
        self.assertEqual(df.loc[1, "nivel_experiencia"], "Entrada / Junior")
        self.assertEqual(transformador.reporte_calidad["cobertura_habilidades_pct"], 100.0)

    def test_elimina_duplicados_y_exporta_reporte(self) -> None:
        transformador = TransformadorDatos("datos")
        transformador.cargar_datos(self.registros + [self.registros[0]])
        transformador.aplicar_limpieza_y_reglas()

        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            transformador.ruta_salida_csv = raiz / "resultado.csv"
            transformador.ruta_salida_parquet = raiz / "resultado.parquet"
            transformador.ruta_reporte = raiz / "calidad.json"
            transformador.exportar_datos_procesados()

            self.assertEqual(len(transformador.dataframe), 2)
            self.assertEqual(transformador.reporte_calidad["duplicados_eliminados"], 1)
            self.assertTrue(transformador.ruta_salida_parquet.exists())
            self.assertTrue(transformador.ruta_reporte.exists())


if __name__ == "__main__":
    unittest.main()
