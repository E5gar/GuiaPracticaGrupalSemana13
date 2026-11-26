from rest_framework import permissions

from resenas.serializers import compro_producto


def es_vendedor(usuario):
    perfil = getattr(usuario, 'perfil', None)
    return perfil is not None and perfil.rol == 'vendedor'


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff or obj.usuario == request.user


class PuedeVender(permissions.BasePermission):
    message = 'Solo administradores o vendedores propietarios.'

    def has_permission(self, request, view):
        usuario = request.user
        return usuario.is_authenticated and (usuario.is_staff or es_vendedor(usuario))

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.vendedor == request.user


class PuedeGestionarOrden(PuedeVender):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.items.filter(producto__vendedor=request.user).exists()


class EsCompradorVerificado(permissions.BasePermission):
    message = 'Solo puede resenar productos que ha comprado.'

    def has_permission(self, request, view):
        producto = str(request.data.get('producto', ''))
        if not producto.isdigit():
            return True
        return compro_producto(request.user, producto)
