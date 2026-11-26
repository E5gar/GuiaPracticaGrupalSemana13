from django.contrib.auth.models import User
from django.core.cache import cache
from rest_framework.test import APITestCase

from productos.models import Categoria, Marca, Producto
from usuarios.models import PerfilUsuario


class BaseAPITest(APITestCase):
    def setUp(self):
        cache.clear()
        self.admin = User.objects.create_superuser('jefe', 'jefe@test.pe', 'clave-test-123')
        self.vendedor = self.crear_usuario('tienda', 'vendedor')
        self.cliente = self.crear_usuario('comprador', 'cliente')
        self.categoria = Categoria.objects.create(nombre='Laptops')
        self.marca = Marca.objects.create(nombre='Dell')
        self.producto = Producto.objects.create(
            sku='T-1', nombre='Laptop de prueba', descripcion='demo', marca=self.marca,
            categoria=self.categoria, precio=1000, descuento=10, stock=5, vendedor=self.vendedor,
        )

    def crear_usuario(self, username, rol):
        usuario = User.objects.create_user(username, password='clave-test-123')
        PerfilUsuario.objects.create(usuario=usuario, rol=rol)
        return usuario
