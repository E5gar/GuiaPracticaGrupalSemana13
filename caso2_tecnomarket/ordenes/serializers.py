from django.db import transaction
from django.db.models import F
from rest_framework import serializers

from carrito.models import Carrito
from productos.models import Producto
from usuarios.models import PerfilUsuario

from .models import ItemOrden, Orden


@transaction.atomic
def crear_orden_desde_carrito(usuario, direccion_envio, metodo_pago):
    carrito = Carrito.objects.select_for_update().filter(usuario=usuario, activo=True).first()
    if carrito is None or not carrito.items.exists():
        raise serializers.ValidationError({'carrito': 'El carrito esta vacio.'})

    orden = Orden.objects.create(
        usuario=usuario,
        direccion_envio=direccion_envio,
        metodo_pago=metodo_pago,
        total=carrito.total_con_descuento,
    )
    for item in carrito.items.select_related('producto'):
        actualizado = Producto.objects.filter(pk=item.producto_id, stock__gte=item.cantidad).update(
            stock=F('stock') - item.cantidad
        )
        if not actualizado:
            raise serializers.ValidationError({'stock': f'Sin stock suficiente de {item.producto.nombre}.'})
        ItemOrden.objects.create(
            orden=orden,
            producto=item.producto,
            cantidad=item.cantidad,
            precio_unitario=item.producto.precio_con_descuento,
        )

    carrito.activo = False
    carrito.save(update_fields=['activo'])
    PerfilUsuario.objects.filter(usuario=usuario).update(puntos=F('puntos') + int(orden.total // 10))
    return orden


class ItemOrdenSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source='producto.nombre', read_only=True)
    importe = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = ItemOrden
        fields = ['producto', 'nombre', 'cantidad', 'precio_unitario', 'importe']


class OrdenSerializer(serializers.ModelSerializer):
    usuario = serializers.CharField(source='usuario.username', read_only=True)
    items = ItemOrdenSerializer(many=True, read_only=True)
    tiempo_estimado_entrega = serializers.SerializerMethodField()

    class Meta:
        model = Orden
        fields = [
            'id', 'usuario', 'items', 'direccion_envio', 'metodo_pago', 'estado', 'total',
            'numero_seguimiento', 'fecha_creacion', 'tiempo_estimado_entrega',
        ]
        read_only_fields = ['estado', 'total', 'numero_seguimiento', 'fecha_creacion']

    def get_tiempo_estimado_entrega(self, obj) -> dict:
        return obj.tiempo_estimado_entrega

    def create(self, validated_data):
        return crear_orden_desde_carrito(**validated_data)


class EstadoOrdenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orden
        fields = ['estado']
        extra_kwargs = {'estado': {'required': True}}

    def validate_estado(self, value):
        if self.instance.estado in (Orden.Estado.CANCELADA, Orden.Estado.ENTREGADA):
            raise serializers.ValidationError('La orden ya esta cerrada.')
        if value == Orden.Estado.CANCELADA:
            raise serializers.ValidationError('Para cancelar use el endpoint cancelar.')
        return value
