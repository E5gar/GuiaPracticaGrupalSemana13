import logging

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

logger = logging.getLogger('throttling')


class RegistroThrottleMixin:
    def throttle_failure(self):
        logger.warning('Limite excedido: scope=%s clave=%s', self.scope, self.key)
        return super().throttle_failure()


class AnonimoThrottle(RegistroThrottleMixin, AnonRateThrottle):
    pass


class UsuarioThrottle(RegistroThrottleMixin, UserRateThrottle):
    pass


class CheckoutRateThrottle(RegistroThrottleMixin, UserRateThrottle):
    scope = 'checkout'


class SearchRateThrottle(RegistroThrottleMixin, UserRateThrottle):
    scope = 'busqueda'

    def allow_request(self, request, view):
        if not request.query_params.get('search'):
            return True
        return super().allow_request(request, view)
