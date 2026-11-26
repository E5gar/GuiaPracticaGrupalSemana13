from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch, Q
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from comun.auditoria import AuditoriaMixin
from comun.permisos import IsOwnerOrReadOnly, es_admin
from prestamos.models import Prestamo

from .serializers import UsuarioListadoSerializer, UsuarioPrivadoSerializer

User = get_user_model()


class UsuarioViewSet(
    AuditoriaMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    http_method_names = ["get", "patch", "head", "options"]
    filterset_fields = ["perfil__tipo", "perfil__carrera"]
    search_fields = ["username", "first_name", "last_name", "email"]
    ordering_fields = ["username", "date_joined"]
    ordering = ["id"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return User.objects.none()
        Prestamo.objects.marcar_vencidos()
        consulta = User.objects.select_related("perfil").annotate(
            total_activos=Count("prestamos", filter=Q(prestamos__estado__in=Prestamo.ESTADOS_ABIERTOS))
        )
        if self.action != "list":
            consulta = consulta.prefetch_related(
                Prefetch("prestamos", queryset=Prestamo.objects.select_related("libro").order_by("-fecha_prestamo"))
            )
        if not es_admin(self.request.user):
            consulta = consulta.filter(pk=self.request.user.pk)
        return consulta

    def get_serializer_class(self):
        if self.action == "list":
            return UsuarioListadoSerializer
        return UsuarioPrivadoSerializer

    def get_permissions(self):
        if self.action == "list":
            return [IsAdminUser()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    @extend_schema(summary="Perfil del usuario autenticado", responses=UsuarioPrivadoSerializer)
    @action(detail=False, methods=["get"])
    def perfil(self, request):
        usuario = self.get_queryset().get(pk=request.user.pk)
        serializer = UsuarioPrivadoSerializer(usuario, context=self.get_serializer_context())
        return Response(serializer.data)