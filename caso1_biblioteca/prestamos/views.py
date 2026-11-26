from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from comun.auditoria import AuditoriaMixin
from comun.paginacion import PaginacionLimitOffset
from comun.permisos import EsBibliotecarioOAdmin, PuedeCrearPrestamo, es_personal
from libros.models import Libro

from .filters import PrestamoFilter
from .models import Prestamo
from .serializers import PrestamoSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Listar préstamos",
        description="El personal ve todos los préstamos. Cada usuario ve solo los suyos. Paginación limit/offset.",
    ),
    create=extend_schema(
        summary="Registrar un préstamo",
        description="Descuenta una unidad del stock. Falla si el usuario ya tiene 5 préstamos abiertos o el libro está agotado.",
        examples=[
            OpenApiExample("Solicitud", value={"usuario": 5, "libro": 12}, request_only=True),
            OpenApiExample(
                "Respuesta",
                value={
                    "id": 31,
                    "usuario": 5,
                    "usuario_nombre": "Lucía Ramos Poma",
                    "libro": 12,
                    "libro_titulo": "Clean Code",
                    "fecha_prestamo": "2026-11-26",
                    "fecha_devolucion": "2026-12-10",
                    "fecha_devuelto": None,
                    "estado": "activo",
                    "dias_restantes": 14,
                    "multa": "0.00",
                },
                response_only=True,
            ),
        ],
    ),
    destroy=extend_schema(summary="Eliminar un préstamo (solo administrador)"),
)
class PrestamoViewSet(AuditoriaMixin, viewsets.ModelViewSet):
    serializer_class = PrestamoSerializer
    filterset_class = PrestamoFilter
    pagination_class = PaginacionLimitOffset
    search_fields = ["libro__titulo", "usuario__username", "usuario__first_name", "usuario__last_name"]
    ordering_fields = ["fecha_prestamo", "fecha_devolucion", "estado"]
    ordering = ["-fecha_prestamo", "-id"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Prestamo.objects.none()
        Prestamo.objects.marcar_vencidos()
        consulta = Prestamo.objects.select_related("usuario", "libro")
        if es_personal(self.request.user):
            return consulta
        return consulta.filter(usuario=self.request.user)

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), PuedeCrearPrestamo()]
        if self.action in ("update", "partial_update", "devolver", "vencidos"):
            return [EsBibliotecarioOAdmin()]
        if self.action == "destroy":
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @extend_schema(summary="Marcar un préstamo como devuelto", request=None, responses=PrestamoSerializer)
    @action(detail=True, methods=["post"])
    def devolver(self, request, pk=None):
        prestamo = self.get_object()
        if prestamo.estado == Prestamo.DEVUELTO:
            return Response({"detail": "Este préstamo ya fue devuelto."}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            libro = Libro.objects.select_for_update().get(pk=prestamo.libro_id)
            libro.stock += 1
            libro.save(update_fields=["stock"])
            prestamo.estado = Prestamo.DEVUELTO
            prestamo.fecha_devuelto = timezone.localdate()
            prestamo.save(update_fields=["estado", "fecha_devuelto"])
        self.registrar("devolver", prestamo)
        serializer = self.get_serializer(prestamo)
        return Response(serializer.data)

    @extend_schema(summary="Listar préstamos vencidos", responses=PrestamoSerializer(many=True))
    @action(detail=False, methods=["get"])
    def vencidos(self, request):
        consulta = self.filter_queryset(self.get_queryset().filter(estado=Prestamo.VENCIDO))
        pagina = self.paginate_queryset(consulta)
        if pagina is not None:
            return self.get_paginated_response(self.get_serializer(pagina, many=True).data)
        return Response(self.get_serializer(consulta, many=True).data)