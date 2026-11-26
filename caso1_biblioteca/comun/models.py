from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Autor(models.Model):
    nombre = models.CharField(max_length=150)
    nacionalidad = models.CharField(max_length=80)
    biografia = models.TextField(blank=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "autores"

    def __str__(self):
        return self.nombre


class Libro(models.Model):
    isbn = models.CharField(max_length=17, unique=True)
    titulo = models.CharField(max_length=250)
    autor = models.ForeignKey(Autor, on_delete=models.PROTECT, related_name="libros")
    editorial = models.CharField(max_length=150)
    anio = models.PositiveSmallIntegerField("año")
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="libros")
    stock = models.PositiveIntegerField(default=0)
    estante = models.CharField(max_length=10)
    piso = models.PositiveSmallIntegerField(default=1)
    portada = models.URLField(blank=True)

    class Meta:
        ordering = ["titulo"]
        indexes = [models.Index(fields=["anio"]), models.Index(fields=["titulo"])]

    def __str__(self):
        return self.titulo

    @property
    def disponible(self):
        return self.stock > 0