from comun.tests import BaseAPITest


class ProductoAPITest(BaseAPITest):
    def test_invitado_ve_catalogo_con_campos_calculados(self):
        respuesta = self.client.get('/api/productos/?categoria=laptops&marca=dell&disponible=true')
        self.assertEqual(respuesta.status_code, 200)
        producto = respuesta.data['results'][0]
        self.assertEqual(producto['precio_con_descuento'], '900.00')
        self.assertTrue(producto['disponible'])

    def test_filtro_por_precio(self):
        respuesta = self.client.get('/api/productos/?precio_min=2000')
        self.assertEqual(respuesta.data['count'], 0)

    def test_cliente_no_puede_crear(self):
        self.client.force_authenticate(self.cliente)
        self.assertEqual(self.client.post('/api/productos/', {}).status_code, 403)

    def test_solo_admin_elimina(self):
        self.client.force_authenticate(self.vendedor)
        url = f'/api/productos/{self.producto.id}/'
        self.assertEqual(self.client.delete(url).status_code, 403)
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.delete(url).status_code, 204)

    def test_limite_para_invitados(self):
        codigos = [self.client.get('/api/productos/').status_code for _ in range(61)]
        self.assertEqual(codigos[-1], 429)
