from django.db.models import Count
from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser

from comun.auditoria import AuditoriaMixin
from comun.permisos import EsBibliotecarioOAdmin

from .filters import LibroFilter
from .models import Autor, Categoria, Libro
from .serializers import AutorSerializer, CategoriaSerializer, LibroSerializer


class PermisosCatalogoMixin:
    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        if self.action == "destroy":
            return [IsAdminUser()]
        return [EsBibliotecarioOAdmin()]


@extend_schema_view(
    list=extend_schema(
        summary="Listar libros",
        description="Catálogo público paginado de 20 en 20. Filtros: categoria, año__gte, año__lte, disponible. Búsqueda por título, autor o ISBN. Orden: título, año, stock.",
    ),
    retrieve=extend_schema(summary="Detalle de un libro"),
    create=extend_schema(
        summary="Registrar un libro",
        examples=[
            OpenApiExample(
                "Nuevo libro",
                value={
                    "isbn": "978-9972-0100-3",
                    "titulo": "Estructuras de datos en Python",
                    "autor_id": 1,
                    "editorial": "Fondo Editorial UNCP",
                    "anio": 2024,
                    "categoria": "programacion",
                    "stock": 4,
                    "estante": "C-14",
                    "piso": 2,
                },
                request_only=True,
            )
        ],
    ),
    destroy=extend_schema(summary="Eliminar un libro (solo administrador)"),
)
class LibroViewSet(PermisosCatalogoMixin, AuditoriaMixin, viewsets.ModelViewSet):
    queryset = Libro.objects.select_related("autor", "categoria")
    serializer_class = LibroSerializer
    filterset_class = LibroFilter
    search_fields = ["titulo", "autor__nombre", "isbn"]
    ordering_fields = ["titulo", "anio", "stock", "autor__nombre"]
    ordering = ["titulo"]


class AutorViewSet(PermisosCatalogoMixin, AuditoriaMixin, viewsets.ModelViewSet):
    queryset = Autor.objects.all()
    serializer_class = AutorSerializer
    search_fields = ["nombre", "nacionalidad"]
    ordering_fields = ["nombre"]


class CategoriaViewSet(PermisosCatalogoMixin, AuditoriaMixin, viewsets.ModelViewSet):
    queryset = Categoria.objects.annotate(total_libros=Count("libros"))
    serializer_class = CategoriaSerializer
    pagination_class = None
    lookup_field = "pk"