from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Resena(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resenas')
    producto = models.ForeignKey('productos.Producto', on_delete=models.CASCADE, related_name='resenas')
    calificacion = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    titulo = models.CharField(max_length=100)
    comentario = models.TextField()
    fecha_creacion = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ['-fecha_creacion', 'id']
        constraints = [
            models.UniqueConstraint(fields=['usuario', 'producto'], name='una_resena_por_producto'),
            models.CheckConstraint(
                condition=models.Q(calificacion__gte=1, calificacion__lte=5),
                name='calificacion_entre_1_y_5',
            ),
        ]

    def __str__(self):
        return f'{self.producto.nombre}: {self.calificacion}/5'
