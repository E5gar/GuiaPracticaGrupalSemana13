from rest_framework.filters import OrderingFilter

ALIAS = {
    "año": "anio",
    "título": "titulo",
    "fecha_préstamo": "fecha_prestamo",
    "fecha_devolución": "fecha_devolucion",
}


class OrdenamientoFlexible(OrderingFilter):
    def get_ordering(self, request, queryset, view):
        parametro = request.query_params.get(self.ordering_param)
        if parametro:
            campos = []
            for campo in parametro.split(","):
                campo = campo.strip()
                signo = "-" if campo.startswith("-") else ""
                nombre = campo.lstrip("-")
                campos.append(signo + ALIAS.get(nombre, nombre))
            ordering = self.remove_invalid_fields(queryset, campos, view, request)
            if ordering:
                return ordering
        return self.get_default_ordering(view)