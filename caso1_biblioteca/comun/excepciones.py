import logging

from rest_framework.exceptions import Throttled
from rest_framework.views import exception_handler

registro = logging.getLogger("throttling")


def manejador(exc, contexto):
    respuesta = exception_handler(exc, contexto)
    if isinstance(exc, Throttled):
        peticion = contexto.get("request")
        usuario = getattr(peticion, "user", None)
        quien = usuario.username if usuario and usuario.is_authenticated else "anonimo"
        ip = peticion.META.get("REMOTE_ADDR", "-") if peticion else "-"
        ruta = peticion.path if peticion else "-"
        registro.warning("429 usuario=%s ip=%s ruta=%s espera=%ss", quien, ip, ruta, exc.wait)
    return respuesta