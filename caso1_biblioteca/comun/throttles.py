from rest_framework.throttling import SimpleRateThrottle


class BurstRateThrottle(SimpleRateThrottle):
    scope = "burst"

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            identificador = request.user.pk
        else:
            identificador = self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": identificador}