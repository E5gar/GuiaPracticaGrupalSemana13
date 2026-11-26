import logging

registro = logging.getLogger("auditoria")


class AuditoriaMixin:
    def registrar(self, accion, instancia):
        usuario = self.request.user
        quien = usuario.username if usuario.is_authenticated else "anonimo"
        registro.info("%s usuario=%s modelo=%s id=%s", accion, quien, instancia.__class__.__name__, instancia.pk)

    def perform_create(self, serializer):
        instancia = serializer.save()
        self.registrar("crear", instancia)

    def perform_update(self, serializer):
        instancia = serializer.save()
        self.registrar("actualizar", instancia)

    def perform_destroy(self, instancia):
        self.registrar("eliminar", instancia)
        instancia.delete()