import unittest

from src.conexion import ClienteComputrabajo, crear_slug


class RespuestaFalsa:
    status_code = 200
    text = "<html><body>Contenido</body></html>"

    def raise_for_status(self) -> None:
        return None


class SesionFalsa:
    def __init__(self) -> None:
        self.url_consultada = ""

    def get(self, url: str, **_: object) -> RespuestaFalsa:
        self.url_consultada = url
        return RespuestaFalsa()


class TestConexion(unittest.TestCase):
    def test_crea_slug_sin_tildes(self) -> None:
        self.assertEqual(crear_slug("Técnico en Farmacia"), "tecnico-en-farmacia")

    def test_conecta_con_url_construida(self) -> None:
        sesion = SesionFalsa()
        cliente = ClienteComputrabajo(sesion=sesion)

        respuesta = cliente.conectar("Analista de Datos", pagina=2)

        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(sesion.url_consultada.endswith("/trabajo-de-analista-de-datos?p=2"))


if __name__ == "__main__":
    unittest.main()
