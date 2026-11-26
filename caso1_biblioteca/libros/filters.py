import django_filters as filters

from .models import Libro


class LibroFilter(filters.FilterSet):
    categoria = filters.CharFilter(field_name="categoria__slug", lookup_expr="iexact")
    año__gte = filters.NumberFilter(field_name="anio", lookup_expr="gte")
    año__lte = filters.NumberFilter(field_name="anio", lookup_expr="lte")
    disponible = filters.BooleanFilter(method="filtrar_disponible")

    class Meta:
        model = Libro
        fields = []

    def filtrar_disponible(self, queryset, nombre, valor):
        if valor is None:
            return queryset
        return queryset.filter(stock__gt=0) if valor else queryset.filter(stock=0)