from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from comun.throttles import CheckoutRateThrottle, UsuarioThrottle
from ordenes.serializers import OrdenSerializer, crear_orden_desde_carrito

from .models import Carrito
from .serializers import (
    AgregarItemSerializer,
    CarritoSerializer,
    CheckoutSerializer,
    EliminarItemSerializer,
)


class CarritoViewSet(viewsets.GenericViewSet):
    serializer_class = CarritoSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    filter_backends = []

    def get_carrito(self):
        carrito, _ = Carrito.objects.get_or_create(usuario=self.request.user, activo=True)
        return carrito

    def responder(self, carrito):
        return Response(CarritoSerializer(carrito).data)

    def list(self, request):
        return self.responder(self.get_carrito())

    @action(detail=False, methods=['post'], serializer_class=AgregarItemSerializer)
    def agregar(self, request):
        carrito = self.get_carrito()
        datos = AgregarItemSerializer(data=request.data, context={'carrito': carrito, 'sumar': True})
        datos.is_valid(raise_exception=True)
        carrito.items.update_or_create(
            producto=datos.validated_data['producto'],
            defaults={'cantidad': datos.validated_data['cantidad_final']},
        )
        if datos.validated_data.get('cupon'):
            carrito.cupon = datos.validated_data['cupon']
            carrito.save(update_fields=['cupon'])
        return self.responder(carrito)

    @action(detail=False, methods=['post'], serializer_class=AgregarItemSerializer)
    def actualizar(self, request):
        carrito = self.get_carrito()
        datos = AgregarItemSerializer(data=request.data, context={'carrito': carrito})
        datos.is_valid(raise_exception=True)
        item = get_object_or_404(carrito.items, producto=datos.validated_data['producto'])
        item.cantidad = datos.validated_data['cantidad']
        item.save(update_fields=['cantidad'])
        return self.responder(carrito)

    @action(detail=False, methods=['post'], serializer_class=EliminarItemSerializer)
    def eliminar(self, request):
        carrito = self.get_carrito()
        datos = EliminarItemSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        get_object_or_404(carrito.items, producto_id=datos.validated_data['producto_id']).delete()
        return self.responder(carrito)

    @action(detail=False, methods=['post'])
    def vaciar(self, request):
        carrito = self.get_carrito()
        carrito.items.all().delete()
        carrito.cupon = ''
        carrito.save(update_fields=['cupon'])
        return self.responder(carrito)

    @action(
        detail=False,
        methods=['post'],
        serializer_class=CheckoutSerializer,
        throttle_classes=[UsuarioThrottle, CheckoutRateThrottle],
    )
    def checkout(self, request):
        datos = CheckoutSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        orden = crear_orden_desde_carrito(request.user, **datos.validated_data)
        return Response(OrdenSerializer(orden).data, status=status.HTTP_201_CREATED)
