import django_filters

from .models import Producto


class ProductoFilter(django_filters.FilterSet):
    categoria = django_filters.CharFilter(field_name='categoria__nombre', lookup_expr='iexact')
    marca = django_filters.CharFilter(field_name='marca__nombre', lookup_expr='iexact')
    precio_min = django_filters.NumberFilter(field_name='precio', lookup_expr='gte')
    precio_max = django_filters.NumberFilter(field_name='precio', lookup_expr='lte')
    disponible = django_filters.BooleanFilter(method='filtrar_disponible')

    class Meta:
        model = Producto
        fields = ['categoria', 'marca', 'precio_min', 'precio_max', 'disponible']

    def filtrar_disponible(self, queryset, name, value):
        return queryset.filter(stock__gt=0) if value else queryset.filter(stock=0)
