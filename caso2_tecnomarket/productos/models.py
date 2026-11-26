from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Categoria(models.Model):
    nombre = models.CharField(max_length=60, unique=True)
    descripcion = models.TextField(blank=True)
    imagen = models.URLField(blank=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Marca(models.Model):
    nombre = models.CharField(max_length=60, unique=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    sku = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT, related_name='productos')
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    descuento = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(90)])
    stock = models.PositiveIntegerField(default=0)
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='productos')
    especificaciones = models.JSONField(default=dict, blank=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-fecha_creacion', 'id']

    def __str__(self):
        return f'{self.sku} - {self.nombre}'

    @property
    def precio_con_descuento(self):
        return (self.precio * (100 - self.descuento) / 100).quantize(Decimal('0.01'))

    @property
    def disponible(self):
        return self.stock > 0


class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    url = models.URLField()

    def __str__(self):
        return self.url
