from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import permissions, viewsets

from .serializers import VendedorSerializer


class VendedorViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VendedorSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = []

    def get_queryset(self):
        return (
            User.objects.filter(Q(perfil__rol='vendedor') | Q(productos__isnull=False))
            .distinct()
            .order_by('id')
        )
