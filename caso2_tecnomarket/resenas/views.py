from rest_framework import mixins, permissions, viewsets

from comun.permisos import EsCompradorVerificado, IsOwnerOrReadOnly

from .models import Resena
from .serializers import ResenaSerializer


class ResenaViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                    mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Resena.objects.select_related('usuario', 'producto')
    serializer_class = ResenaSerializer
    filterset_fields = ['producto', 'calificacion']
    ordering_fields = ['calificacion', 'fecha_creacion']

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated(), EsCompradorVerificado()]
        if self.action == 'destroy':
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)
