from django.db.models import Avg
from rest_framework import serializers

from .models import Categoria, ImagenProducto, Marca, Producto


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'imagen']


class ImagenProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenProducto
        fields = ['id', 'url']


class ProductoSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='producto-detail')
    marca = serializers.SlugRelatedField(slug_field='nombre', queryset=Marca.objects.all())
    categoria = CategoriaSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        source='categoria', queryset=Categoria.objects.all(), write_only=True
    )
    imagenes = ImagenProductoSerializer(many=True, read_only=True)
    precio_con_descuento = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    disponible = serializers.BooleanField(read_only=True)
    rating_promedio = serializers.SerializerMethodField()
    vendedor = serializers.HyperlinkedRelatedField(view_name='vendedor-detail', read_only=True)
    resenas = serializers.HyperlinkedRelatedField(view_name='resena-detail', many=True, read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id', 'url', 'sku', 'nombre', 'descripcion', 'marca', 'categoria', 'categoria_id',
            'precio', 'descuento', 'precio_con_descuento', 'stock', 'disponible',
            'rating_promedio', 'imagenes', 'especificaciones', 'vendedor', 'resenas',
            'fecha_creacion',
        ]
        read_only_fields = ['fecha_creacion']

    def get_rating_promedio(self, obj) -> float:
        if hasattr(obj, 'rating_promedio'):
            promedio = obj.rating_promedio
        else:
            promedio = obj.resenas.aggregate(valor=Avg('calificacion'))['valor']
        return round(float(promedio or 0), 2)
