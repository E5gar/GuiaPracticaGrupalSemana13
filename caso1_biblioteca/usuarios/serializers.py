from django.contrib.auth import get_user_model
from rest_framework import serializers

from prestamos.serializers import PrestamoResumenSerializer

User = get_user_model()


class UsuarioPublicoSerializer(serializers.ModelSerializer):
    nombre = serializers.SerializerMethodField()
    tipo = serializers.CharField(source="perfil.tipo", read_only=True)
    carrera = serializers.CharField(source="perfil.carrera", read_only=True)

    class Meta:
        model = User
        fields = ["id", "nombre", "tipo", "carrera"]

    def get_nombre(self, obj) -> str:
        return obj.get_full_name() or obj.username


class UsuarioListadoSerializer(UsuarioPublicoSerializer):
    prestamos_activos = serializers.IntegerField(source="total_activos", read_only=True)

    class Meta(UsuarioPublicoSerializer.Meta):
        fields = ["id", "username", "nombre", "tipo", "carrera", "prestamos_activos"]


class UsuarioPrivadoSerializer(UsuarioPublicoSerializer):
    email = serializers.EmailField(required=False)
    telefono = serializers.CharField(source="perfil.telefono", required=False, allow_blank=True, max_length=20)
    carnet = serializers.CharField(source="perfil.carnet", read_only=True)
    prestamos_activos = serializers.IntegerField(source="total_activos", read_only=True)
    historial_prestamos = PrestamoResumenSerializer(source="prestamos", many=True, read_only=True)

    class Meta(UsuarioPublicoSerializer.Meta):
        fields = [
            "id",
            "username",
            "nombre",
            "tipo",
            "carrera",
            "email",
            "telefono",
            "carnet",
            "prestamos_activos",
            "historial_prestamos",
        ]
        read_only_fields = ["username"]

    def update(self, instance, validated_data):
        datos_perfil = validated_data.pop("perfil", {})
        for campo, valor in validated_data.items():
            setattr(instance, campo, valor)
        instance.save()
        for campo, valor in datos_perfil.items():
            setattr(instance.perfil, campo, valor)
        instance.perfil.save()
        return instance