from django.conf import settings
from django.db import models


class Perfil(models.Model):
    TIPOS = [
        ("administrador", "Administrador"),
        ("bibliotecario", "Bibliotecario"),
        ("estudiante", "Estudiante"),
        ("docente", "Docente"),
        ("investigador", "Investigador"),
    ]

    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfil")
    tipo = models.CharField(max_length=20, choices=TIPOS, default="estudiante")
    carrera = models.CharField(max_length=120, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    carnet = models.CharField(max_length=12, blank=True)

    def __str__(self):
        return f"{self.usuario.username} ({self.get_tipo_display()})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.tipo == "administrador" and not self.usuario.is_staff:
            self.usuario.is_staff = True
            self.usuario.save(update_fields=["is_staff"])