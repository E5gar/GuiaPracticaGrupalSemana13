from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from carrito.views import CarritoViewSet
from config import documentacion
from ordenes.views import OrdenViewSet
from productos.views import ProductoViewSet
from resenas.views import ResenaViewSet
from usuarios.views import VendedorViewSet

router = DefaultRouter()
router.register('productos', ProductoViewSet, basename='producto')
router.register('carrito', CarritoViewSet, basename='carrito')
router.register('ordenes', OrdenViewSet, basename='orden')
router.register('rese\u00f1as', ResenaViewSet, basename='resena')
router.register('vendedores', VendedorViewSet, basename='vendedor')

urlpatterns = [
    path('auth/token/', obtain_auth_token, name='token'),
    path('', include(router.urls)),
]
