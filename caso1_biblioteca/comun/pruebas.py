from django.contrib.auth import get_user_model

User = get_user_model()


def crear_usuario(nombre, tipo=None, superusuario=False):
    if superusuario:
        usuario = User.objects.create_superuser(nombre, f"{nombre}@uncp.edu.pe", "clave12345")
    else:
        usuario = User.objects.create_user(nombre, f"{nombre}@uncp.edu.pe", "clave12345")
    if tipo:
        usuario.perfil.tipo = tipo
        usuario.perfil.save()
    return usuario