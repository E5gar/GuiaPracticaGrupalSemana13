from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


def token_vencido(token):
    return timezone.now() - token.created > timedelta(hours=settings.TOKEN_VIDA_HORAS)


class TokenConExpiracion(TokenAuthentication):
    def authenticate_credentials(self, key):
        usuario, token = super().authenticate_credentials(key)
        if token_vencido(token):
            token.delete()
            raise AuthenticationFailed("El token expiró, vuelve a iniciar sesión.")
        return usuario, token