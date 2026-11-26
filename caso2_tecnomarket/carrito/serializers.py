from rest_framework import serializers

from ordenes.models import Orden
from productos.models import Producto

from .models import CUPONES, Carrito, ItemCarrito


class ItemCarritoSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source='producto.nombre', read_only=True)
    precio_unitario = serializers.DecimalField(
        source='producto.precio_con_descuento', max_digits=10, decimal_places=2, read_only=True
    )
    importe = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = ItemCarrito
        fields = ['producto', 'nombre', 'precio_unitario', 'cantidad', 'importe']


class CarritoSerializer(serializers.ModelSerializer):
    usuario = serializers.CharField(source='usuario.username', read_only=True)
    items = ItemCarritoSerializer(many=True, read_only=True)
    cantidad_items = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    impuestos = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_con_descuento = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Carrito
        fields = [
            'id', 'usuario', 'items', 'cupon', 'cantidad_items', 'subtotal',
            'impuestos', 'total', 'total_con_descuento',
        ]


class AgregarItemSerializer(serializers.Serializer):
    producto_id = serializers.PrimaryKeyRelatedField(source='producto', queryset=Producto.objects.all())
    cantidad = serializers.IntegerField(min_value=1, default=1)
    cupon = serializers.CharField(required=False, allow_blank=True, max_length=20)

    def validate_cupon(self, value):
        if value and value.upper() not in CUPONES:
            raise serializers.ValidationError('El cupon no existe.')
        return value.upper()

    def validate(self, attrs):
        producto = attrs['producto']
        cantidad = attrs['cantidad']
        if self.context.get('sumar'):
            item = self.context['carrito'].items.filter(producto=producto).first()
            cantidad += item.cantidad if item else 0
        if cantidad > producto.stock:
            raise serializers.ValidationError({'cantidad': f'Solo hay {producto.stock} unidades en stock.'})
        attrs['cantidad_final'] = cantidad
        return attrs


class EliminarItemSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField()


class CheckoutSerializer(serializers.Serializer):
    direccion_envio = serializers.CharField(max_length=200)
    metodo_pago = serializers.ChoiceField(choices=Orden.MetodoPago.choices)
