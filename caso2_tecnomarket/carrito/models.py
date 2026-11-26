from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

IGV = Decimal('0.18')
CUPONES = {'BIENVENIDA10': 10, 'CYBER20': 20}
CENTIMOS = Decimal('0.01')


class Carrito(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carritos')
    activo = models.BooleanField(default=True)
    cupon = models.CharField(max_length=20, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['usuario'],
                condition=models.Q(activo=True),
                name='un_carrito_activo_por_usuario',
            ),
        ]

    def __str__(self):
        return f'Carrito {self.pk} de {self.usuario}'

    @property
    def subtotal(self):
        return sum((item.importe for item in self.items.all()), Decimal('0.00'))

    @property
    def impuestos(self):
        return (self.subtotal * IGV).quantize(CENTIMOS)

    @property
    def total(self):
        return self.subtotal + self.impuestos

    @property
    def total_con_descuento(self):
        porcentaje = CUPONES.get(self.cupon.upper(), 0)
        return (self.total * (100 - porcentaje) / 100).quantize(CENTIMOS)

    @property
    def cantidad_items(self):
        return sum(item.cantidad for item in self.items.all())


class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey('productos.Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['carrito', 'producto'], name='producto_unico_por_carrito'),
        ]

    def __str__(self):
        return f'{self.cantidad} x {self.producto.nombre}'

    @property
    def importe(self):
        return self.producto.precio_con_descuento * self.cantidad
