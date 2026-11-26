from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Perfil

User = get_user_model()


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False


class UsuarioAdmin(UserAdmin):
    inlines = [PerfilInline]
    list_display = ("username", "first_name", "last_name", "email", "is_staff")

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []
        return super().get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, UsuarioAdmin)