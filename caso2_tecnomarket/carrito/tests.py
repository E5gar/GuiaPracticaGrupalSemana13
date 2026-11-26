from comun.tests import BaseAPITest


class CarritoAPITest(BaseAPITest):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(self.cliente)

    def agregar(self, cantidad):
        return self.client.post('/api/carrito/agregar/', {'producto_id': self.producto.id, 'cantidad': cantidad})

    def test_no_supera_el_stock(self):
        self.assertEqual(self.agregar(6).status_code, 400)

    def test_checkout_descuenta_stock_y_cancelar_lo_devuelve(self):
        self.agregar(2)
        orden = self.client.post('/api/carrito/checkout/', {'direccion_envio': 'Huancayo', 'metodo_pago': 'culqi'})
        self.assertEqual(orden.status_code, 201)
        self.assertEqual(orden.data['total'], '2124.00')
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 3)
        self.client.post(f"/api/ordenes/{orden.data['id']}/cancelar/")
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 5)
