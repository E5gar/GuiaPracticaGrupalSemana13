from rest_framework.permissions import SAFE_METHODS, BasePermission


def es_admin(usuario):
    return bool(usuario and usuario.is_authenticated and (usuario.is_staff or usuario.is_superuser))


def tipo_de(usuario):
    perfil = getattr(usuario, "perfil", None)
    return getattr(perfil, "tipo", None)


def es_bibliotecario(usuario):
    return bool(usuario and usuario.is_authenticated and tipo_de(usuario) == "bibliotecario")


def es_personal(usuario):
    return es_admin(usuario) or es_bibliotecario(usuario)


class EsBibliotecarioOAdmin(BasePermission):
    message = "Solo el personal de la biblioteca puede realizar esta acción."

    def has_permission(self, request, view):
        return es_personal(request.user)


class IsOwnerOrReadOnly(BasePermission):
    message = "Solo el propietario puede modificar este recurso."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        propietario = getattr(obj, "usuario", obj)
        return es_admin(request.user) or propietario == request.user


class PuedeCrearPrestamo(BasePermission):
    message = "El usuario ya tiene el máximo de préstamos activos."

    def has_permission(self, request, view):
        if not es_personal(request.user):
            self.message = "Solo el personal de la biblioteca puede registrar préstamos."
            return False
        if request.method != "POST":
            return True
        from prestamos.models import Prestamo

        try:
            usuario_id = int(request.data.get("usuario"))
        except (TypeError, ValueError, AttributeError):
            return True
        abiertos = Prestamo.objects.filter(usuario_id=usuario_id, estado__in=Prestamo.ESTADOS_ABIERTOS).count()
        if abiertos >= Prestamo.MAX_ACTIVOS:
            self.message = f"El usuario ya tiene {Prestamo.MAX_ACTIVOS} préstamos activos, que es el máximo permitido."
            return False
        return True