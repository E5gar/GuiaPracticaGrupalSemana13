from django.db import transaction
from django.db.models import F
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from comun.paginacion import PaginacionOrdenes
from comun.permisos import PuedeGestionarOrden
from comun.throttles import CheckoutRateThrottle, UsuarioThrottle
from productos.models import Producto

from .models import Orden
from .serializers import EstadoOrdenSerializer, OrdenSerializer


class OrdenViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                   mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = OrdenSerializer
    pagination_class = PaginacionOrdenes
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['estado', 'metodo_pago']
    ordering_fields = ['fecha_creacion', 'total']

    def get_queryset(self):
        consulta = Orden.objects.select_related('usuario').prefetch_related('items__producto')
        if getattr(self, 'swagger_fake_view', False):
            return consulta.none()
        usuario = self.request.user
        if usuario.is_staff:
            return consulta
        if self.action == 'partial_update':
            return consulta.filter(items__producto__vendedor=usuario).distinct()
        return consulta.filter(usuario=usuario)

    def get_permissions(self):
        if self.action == 'partial_update':
            return [PuedeGestionarOrden()]
        return super().get_permissions()

    def get_throttles(self):
        if self.action == 'create':
            return [UsuarioThrottle(), CheckoutRateThrottle()]
        return super().get_throttles()

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return EstadoOrdenSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    def partial_update(self, request, pk=None):
        orden = self.get_object()
        datos = EstadoOrdenSerializer(orden, data=request.data)
        datos.is_valid(raise_exception=True)
        datos.save()
        return Response(OrdenSerializer(orden).data)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def cancelar(self, request, pk=None):
        orden = self.get_object()
        if orden.estado != Orden.Estado.PENDIENTE:
            return Response(
                {'detail': 'Solo se pueden cancelar ordenes pendientes.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        for item in orden.items.all():
            Producto.objects.filter(pk=item.producto_id).update(stock=F('stock') + item.cantidad)
        orden.estado = Orden.Estado.CANCELADA
        orden.save(update_fields=['estado'])
        return Response(OrdenSerializer(orden).data)

    @action(detail=False, url_path='mis-ordenes')
    def mis_ordenes(self, request):
        consulta = self.filter_queryset(self.get_queryset().filter(usuario=request.user))
        pagina = self.paginate_queryset(consulta)
        return self.get_paginated_response(self.get_serializer(pagina, many=True).data)
