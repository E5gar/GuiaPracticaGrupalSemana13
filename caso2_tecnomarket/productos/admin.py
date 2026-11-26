from django.contrib import admin

from .models import Categoria, ImagenProducto, Marca, Producto


class ImagenInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('sku', 'nombre', 'marca', 'categoria', 'precio', 'descuento', 'stock')
    list_filter = ('categoria', 'marca')
    search_fields = ('sku', 'nombre')
    inlines = [ImagenInline]


admin.site.register(Categoria)
admin.site.register(Marca)
