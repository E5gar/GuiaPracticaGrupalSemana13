import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Orden(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        PAGADA = 'pagada', 'Pagada'
        ENVIADA = 'enviada', 'Enviada'
        ENTREGADA = 'entregada', 'Entregada'
        CANCELADA = 'cancelada', 'Cancelada'

    class MetodoPago(models.TextChoices):
        CULQI = 'culqi', 'Culqi'
        MERCADOPAGO = 'mercadopago', 'MercadoPago'
        NIUBIZ = 'niubiz', 'Niubiz'

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ordenes')
    direccion_envio = models.CharField(max_length=200)
    metodo_pago = models.CharField(max_length=15, choices=MetodoPago.choices)
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.PENDIENTE)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    numero_seguimiento = models.CharField(max_length=20, blank=True, editable=False)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-fecha_creacion', 'id']

    def __str__(self):
        return f'Orden {self.pk} - {self.estado}'

    def save(self, *args, **kwargs):
        enviada = self.estado in (self.Estado.ENVIADA, self.Estado.ENTREGADA)
        if enviada and not self.numero_seguimiento:
            self.numero_seguimiento = f'TM-{uuid.uuid4().hex[:10].upper()}'
        super().save(*args, **kwargs)

    @property
    def tiempo_estimado_entrega(self):
        desde = (self.fecha_creacion + timedelta(days=3)).date()
        hasta = (self.fecha_creacion + timedelta(days=5)).date()
        return {'desde': desde, 'hasta': hasta}


class ItemOrden(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey('productos.Producto', on_delete=models.PROTECT, related_name='items_orden')
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.cantidad} x {self.producto.nombre}'

    @property
    def importe(self):
        return self.precio_unitario * self.cantidad
