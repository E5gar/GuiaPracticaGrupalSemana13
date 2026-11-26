from rest_framework import serializers

from ordenes.models import ItemOrden, Orden

from .models import Resena


def compro_producto(usuario, producto):
    return ItemOrden.objects.filter(
        orden__usuario=usuario,
        producto=producto,
        orden__estado__in=[Orden.Estado.PAGADA, Orden.Estado.ENVIADA, Orden.Estado.ENTREGADA],
    ).exists()


class ResenaSerializer(serializers.ModelSerializer):
    usuario = serializers.CharField(source='usuario.username', read_only=True)
    es_compra_verificada = serializers.SerializerMethodField()

    class Meta:
        model = Resena
        fields = [
            'id', 'usuario', 'producto', 'calificacion', 'titulo', 'comentario',
            'fecha_creacion', 'es_compra_verificada',
        ]
        read_only_fields = ['fecha_creacion']

    def get_es_compra_verificada(self, obj) -> bool:
        return compro_producto(obj.usuario, obj.producto)

    def validate_calificacion(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError('La calificacion debe estar entre 1 y 5.')
        return value

    def validate(self, attrs):
        usuario = self.context['request'].user
        producto = attrs['producto']
        if not compro_producto(usuario, producto):
            raise serializers.ValidationError('Solo puede resenar productos que ha comprado.')
        if Resena.objects.filter(usuario=usuario, producto=producto).exists():
            raise serializers.ValidationError('Ya reseno este producto.')
        return attrs
