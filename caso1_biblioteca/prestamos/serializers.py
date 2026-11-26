from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from libros.models import Libro

from .models import Prestamo


class PrestamoSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="prestamo-detail")
    usuario_nombre = serializers.SerializerMethodField()
    libro_titulo = serializers.CharField(source="libro.titulo", read_only=True)
    dias_restantes = serializers.IntegerField(read_only=True)
    multa = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)

    class Meta:
        model = Prestamo
        fields = [
            "id",
            "url",
            "usuario",
            "usuario_nombre",
            "libro",
            "libro_titulo",
            "fecha_prestamo",
            "fecha_devolucion",
            "fecha_devuelto",
            "estado",
            "dias_restantes",
            "multa",
        ]
        read_only_fields = ["fecha_prestamo", "fecha_devuelto", "estado"]
        extra_kwargs = {"fecha_devolucion": {"required": False}}

    def get_usuario_nombre(self, obj) -> str:
        return obj.usuario.get_full_name() or obj.usuario.username

    def validate(self, attrs):
        hoy = timezone.localdate()
        fecha = attrs.get("fecha_devolucion")
        base = self.instance.fecha_prestamo if self.instance else hoy
        if fecha and fecha < base:
            raise serializers.ValidationError({"fecha_devolucion": "La fecha de devolución no puede ser anterior al préstamo."})
        if self.instance is None:
            usuario = attrs["usuario"]
            libro = attrs["libro"]
            abiertos = Prestamo.objects.filter(usuario=usuario, estado__in=Prestamo.ESTADOS_ABIERTOS).count()
            if abiertos >= Prestamo.MAX_ACTIVOS:
                raise serializers.ValidationError(
                    {"usuario": f"El usuario ya tiene {Prestamo.MAX_ACTIVOS} préstamos activos, que es el máximo permitido."}
                )
            if libro.stock < 1:
                raise serializers.ValidationError({"libro": "El libro no tiene ejemplares disponibles."})
            attrs.setdefault("fecha_devolucion", hoy + timedelta(days=Prestamo.DIAS_PRESTAMO))
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            libro = Libro.objects.select_for_update().get(pk=validated_data["libro"].pk)
            if libro.stock < 1:
                raise serializers.ValidationError({"libro": "El libro no tiene ejemplares disponibles."})
            libro.stock -= 1
            libro.save(update_fields=["stock"])
            return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("usuario", None)
        validated_data.pop("libro", None)
        return super().update(instance, validated_data)


class PrestamoResumenSerializer(serializers.ModelSerializer):
    libro_titulo = serializers.CharField(source="libro.titulo", read_only=True)
    dias_restantes = serializers.IntegerField(read_only=True)
    multa = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)

    class Meta:
        model = Prestamo
        fields = [
            "id",
            "libro_titulo",
            "fecha_prestamo",
            "fecha_devolucion",
            "fecha_devuelto",
            "estado",
            "dias_restantes",
            "multa",
        ]