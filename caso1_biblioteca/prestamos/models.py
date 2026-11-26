from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class PrestamoQuerySet(models.QuerySet):
    def marcar_vencidos(self):
        return self.filter(estado="activo", fecha_devolucion__lt=timezone.localdate()).update(estado="vencido")


class Prestamo(models.Model):
    ACTIVO = "activo"
    DEVUELTO = "devuelto"
    VENCIDO = "vencido"
    ESTADOS = [(ACTIVO, "Activo"), (DEVUELTO, "Devuelto"), (VENCIDO, "Vencido")]
    ESTADOS_ABIERTOS = (ACTIVO, VENCIDO)

    MAX_ACTIVOS = 5
    DIAS_PRESTAMO = 14
    MULTA_POR_DIA = Decimal("2.00")

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="prestamos")
    libro = models.ForeignKey("libros.Libro", on_delete=models.PROTECT, related_name="prestamos")
    fecha_prestamo = models.DateField(default=timezone.localdate)
    fecha_devolucion = models.DateField()
    fecha_devuelto = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default=ACTIVO)

    objects = PrestamoQuerySet.as_manager()

    class Meta:
        ordering = ["-fecha_prestamo", "-id"]
        indexes = [models.Index(fields=["estado"]), models.Index(fields=["usuario", "estado"])]

    def __str__(self):
        return f"{self.usuario} - {self.libro} ({self.estado})"

    @property
    def dias_restantes(self):
        if self.estado == self.DEVUELTO:
            return None
        return (self.fecha_devolucion - timezone.localdate()).days

    @property
    def dias_atraso(self):
        fin = self.fecha_devuelto or timezone.localdate()
        return max((fin - self.fecha_devolucion).days, 0)

    @property
    def multa(self):
        return self.MULTA_POR_DIA * self.dias_atraso