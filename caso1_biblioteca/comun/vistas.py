from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from django.conf import settings

from .autenticacion import token_vencido
from .permisos import es_admin, es_bibliotecario, tipo_de


def datos_usuario(usuario):
    return {
        "id": usuario.pk,
        "username": usuario.username,
        "nombre": usuario.get_full_name() or usuario.username,
        "tipo": tipo_de(usuario),
        "es_admin": es_admin(usuario),
        "es_bibliotecario": es_bibliotecario(usuario),
    }


class LoginView(ObtainAuthToken):
    authentication_classes = ()
    throttle_classes = api_settings.DEFAULT_THROTTLE_CLASSES

    @extend_schema(
        summary="Obtener token de acceso",
        description="Devuelve el token que debe enviarse como Authorization: Token <token>. Expira a las 12 horas.",
        examples=[
            OpenApiExample("Solicitud", value={"username": "lucia.ramos", "password": "Uncp2026!"}, request_only=True),
            OpenApiExample(
                "Respuesta",
                value={
                    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
                    "expira_en_horas": 12,
                    "usuario": {
                        "id": 5,
                        "username": "lucia.ramos",
                        "nombre": "Lucía Ramos Poma",
                        "tipo": "estudiante",
                        "es_admin": False,
                        "es_bibliotecario": False,
                    },
                },
                response_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        usuario = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=usuario)
        if token_vencido(token):
            token.delete()
            token = Token.objects.create(user=usuario)
        return Response(
            {
                "token": token.key,
                "expira_en_horas": settings.TOKEN_VIDA_HORAS,
                "usuario": datos_usuario(usuario),
            }
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Cerrar sesión y revocar el token", request=None, responses={204: None})
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)