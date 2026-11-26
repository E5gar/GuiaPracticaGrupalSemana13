from rest_framework import serializers

from .models import Autor, Categoria, Libro


class AutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Autor
        fields = ["id", "nombre", "nacionalidad", "biografia"]


class CategoriaSerializer(serializers.ModelSerializer):
    total_libros = serializers.IntegerField(read_only=True)

    class Meta:
        model = Categoria
        fields = ["id", "nombre", "slug", "total_libros"]


class LibroSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="libro-detail")
    autor = AutorSerializer(read_only=True)
    autor_id = serializers.PrimaryKeyRelatedField(queryset=Autor.objects.all(), source="autor", write_only=True)
    categoria = serializers.SlugRelatedField(slug_field="slug", queryset=Categoria.objects.all())
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)
    disponible = serializers.SerializerMethodField()
    ubicacion = serializers.SerializerMethodField()

    class Meta:
        model = Libro
        fields = [
            "id",
            "url",
            "isbn",
            "titulo",
            "autor",
            "autor_id",
            "editorial",
            "anio",
            "categoria",
            "categoria_nombre",
            "stock",
            "estante",
            "piso",
            "ubicacion",
            "portada",
            "disponible",
        ]

    def get_disponible(self, obj) -> bool:
        return obj.stock > 0

    def get_ubicacion(self, obj) -> str:
        return f"Estante {obj.estante} · Piso {obj.piso}"