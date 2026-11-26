from rest_framework.test import APITestCase

from comun.pruebas import crear_usuario


class UsuarioApiTests(APITestCase):
    def setUp(self):
        self.estudiante = crear_usuario("estudiante", "estudiante")
        self.otro = crear_usuario("otro", "estudiante")
        self.admin = crear_usuario("admin", superusuario=True)

    def test_listado_solo_admin(self):
        self.client.force_authenticate(self.estudiante)
        self.assertEqual(self.client.get("/api/usuarios/").status_code, 403)
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.get("/api/usuarios/").status_code, 200)

    def test_perfil_del_autenticado(self):
        self.client.force_authenticate(self.estudiante)
        respuesta = self.client.get("/api/usuarios/perfil/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["username"], "estudiante")
        self.assertEqual(respuesta.data["prestamos_activos"], 0)

    def test_no_ve_a_otros_usuarios(self):
        self.client.force_authenticate(self.estudiante)
        self.assertEqual(self.client.get(f"/api/usuarios/{self.otro.pk}/").status_code, 404)

    def test_actualiza_su_telefono(self):
        self.client.force_authenticate(self.estudiante)
        respuesta = self.client.patch(f"/api/usuarios/{self.estudiante.pk}/", {"telefono": "987654321"}, format="json")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["telefono"], "987654321")