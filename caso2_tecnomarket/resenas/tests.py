from comun.tests import BaseAPITest


class ResenaAPITest(BaseAPITest):
    def test_solo_compradores_pueden_resenar(self):
        self.client.force_authenticate(self.cliente)
        datos = {'producto': self.producto.id, 'calificacion': 5, 'titulo': 'Bien', 'comentario': 'Todo ok'}
        respuesta = self.client.post('/api/rese\u00f1as/', datos)
        self.assertEqual(respuesta.status_code, 403)
