import django_filters as filters

from .models import Prestamo


class PrestamoFilter(filters.FilterSet):
    class Meta:
        model = Prestamo
        fields = {
            "estado": ["exact"],
            "usuario": ["exact"],
            "libro": ["exact"],
            "fecha_prestamo": ["gte", "lte"],
        }