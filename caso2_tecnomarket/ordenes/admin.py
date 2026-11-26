from django.contrib import admin

from .models import ItemOrden, Orden


class ItemOrdenInline(admin.TabularInline):
    model = ItemOrden
    extra = 0


@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'estado', 'total', 'numero_seguimiento', 'fecha_creacion')
    list_filter = ('estado', 'metodo_pago')
    inlines = [ItemOrdenInline]
