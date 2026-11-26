from django.conf import settings
from django.db import models


class PerfilUsuario(models.Model):
    class Rol(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        VENDEDOR = 'vendedor', 'Vendedor'
        CLIENTE = 'cliente', 'Cliente'

    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=10, choices=Rol.choices, default=Rol.CLIENTE)
    telefono = models.CharField(max_length=15, blank=True)
    puntos = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.usuario.username} ({self.rol})'
