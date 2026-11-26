from rest_framework.routers import DefaultRouter

from libros.views import AutorViewSet, CategoriaViewSet, LibroViewSet
from prestamos.views import PrestamoViewSet
from usuarios.views import UsuarioViewSet

router = DefaultRouter()
router.register("libros", LibroViewSet, basename="libro")
router.register("autores", AutorViewSet, basename="autor")
router.register("categorias", CategoriaViewSet, basename="categoria")
router.register("prestamos", PrestamoViewSet, basename="prestamo")
router.register("usuarios", UsuarioViewSet, basename="usuario")

urlpatterns = router.urls