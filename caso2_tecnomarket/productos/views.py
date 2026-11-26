from django.db.models import Avg, FloatField, Value
from django.db.models.functions import Coalesce
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from comun.permisos import PuedeVender
from comun.throttles import AnonimoThrottle, SearchRateThrottle, UsuarioThrottle
from resenas.serializers import ResenaSerializer

from .filters import ProductoFilter
from .models import Producto
from .serializers import ProductoSerializer


class ProductoViewSet(viewsets.ModelViewSet):
    serializer_class = ProductoSerializer
    filterset_class = ProductoFilter
    search_fields = ['nombre', 'descripcion', 'marca__nombre']
    ordering_fields = ['precio', 'rating_promedio', 'fecha_creacion']
    throttle_classes = [AnonimoThrottle, UsuarioThrottle, SearchRateThrottle]

    def get_queryset(self):
        return (
            Producto.objects.select_related('marca', 'categoria', 'vendedor')
            .prefetch_related('imagenes', 'resenas')
            .annotate(rating_promedio=Coalesce(Avg('resenas__calificacion'), Value(0.0), output_field=FloatField()))
            .order_by('-fecha_creacion', 'id')
        )

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update'):
            return [PuedeVender()]
        if self.action == 'destroy':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(vendedor=self.request.user)

    @action(detail=True, url_path='rese\u00f1as', url_name='resenas', serializer_class=ResenaSerializer)
    def resenas(self, request, pk=None):
        consulta = self.get_object().resenas.select_related('usuario')
        pagina = self.paginate_queryset(consulta)
        if pagina is not None:
            return self.get_paginated_response(self.get_serializer(pagina, many=True).data)
        return Response(self.get_serializer(consulta, many=True).data)
