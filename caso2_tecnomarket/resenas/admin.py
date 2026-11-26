from django.contrib import admin

from .models import Resena


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ('producto', 'usuario', 'calificacion', 'fecha_creacion')
    list_filter = ('calificacion',)
