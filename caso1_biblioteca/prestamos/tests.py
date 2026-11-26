from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APITestCase

from comun.pruebas import crear_usuario
from libros.models import Autor, Categoria, Libro

from .models import Prestamo


class PrestamoApiTests(APITestCase):
    def setUp(self):
        autor = Autor.objects.create(nombre="Autor", nacionalidad="Peruana")
        categoria = Categoria.objects.create(nombre="Ingeniería", slug="ingenieria")
        self.libro = self.nuevo_libro("L1", 2, autor, categoria)
        self.agotado = self.nuevo_libro("L2", 0, autor, categoria)
        self.estudiante = crear_usuario("estudiante", "estudiante")
        self.otro = crear_usuario("otro", "estudiante")
        self.bibliotecario = crear_usuario("bibliotecario", "bibliotecario")

    def nuevo_libro(self, titulo, stock, autor, categoria):
        return Libro.objects.create(
            isbn=titulo,
            titulo=titulo,
            autor=autor,
            editorial="UNCP",
            anio=2020,
            categoria=categoria,
            stock=stock,
            estante="A-1",
            piso=1,
        )

    def prestamo_directo(self, **extra):
        hoy = timezone.localdate()
        datos = {
            "usuario": self.estudiante,
            "libro": self.libro,
            "fecha_prestamo": hoy,
            "fecha_devolucion": hoy + timedelta(days=14),
        }
        datos.update(extra)
        return Prestamo.objects.create(**datos)

    def test_bibliotecario_registra_y_descuenta_stock(self):
        self.client.force_authenticate(self.bibliotecario)
        respuesta = self.client.post("/api/prestamos/", {"usuario": self.estudiante.pk, "libro": self.libro.pk}, format="json")
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.data["estado"], "activo")
        self.libro.refresh_from_db()
        self.assertEqual(self.libro.stock, 1)

    def test_estudiante_no_registra_prestamos(self):
        self.client.force_authenticate(self.estudiante)
        respuesta = self.client.post("/api/prestamos/", {"usuario": self.estudiante.pk, "libro": self.libro.pk}, format="json")
        self.assertEqual(respuesta.status_code, 403)

    def test_no_permite_mas_de_cinco_activos(self):
        for _ in range(5):
            self.prestamo_directo()
        self.client.force_authenticate(self.bibliotecario)
        respuesta = self.client.post("/api/prestamos/", {"usuario": self.estudiante.pk, "libro": self.libro.pk}, format="json")
        self.assertEqual(respuesta.status_code, 403)

    def test_no_permite_libro_sin_stock(self):
        self.client.force_authenticate(self.bibliotecario)
        respuesta = self.client.post("/api/prestamos/", {"usuario": self.estudiante.pk, "libro": self.agotado.pk}, format="json")
        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("libro", respuesta.data)

    def test_devolver_repone_stock_y_no_se_repite(self):
        self.client.force_authenticate(self.bibliotecario)
        creado = self.client.post("/api/prestamos/", {"usuario": self.estudiante.pk, "libro": self.libro.pk}, format="json")
        ruta = f"/api/prestamos/{creado.data['id']}/devolver/"
        primera = self.client.post(ruta)
        self.assertEqual(primera.status_code, 200)
        self.assertEqual(primera.data["estado"], "devuelto")
        self.libro.refresh_from_db()
        self.assertEqual(self.libro.stock, 2)
        self.assertEqual(self.client.post(ruta).status_code, 400)

    def test_multa_de_dos_soles_por_dia(self):
        hoy = timezone.localdate()
        prestamo = self.prestamo_directo(fecha_prestamo=hoy - timedelta(days=17), fecha_devolucion=hoy - timedelta(days=3))
        self.client.force_authenticate(self.estudiante)
        respuesta = self.client.get(f"/api/prestamos/{prestamo.pk}/")
        self.assertEqual(respuesta.data["estado"], "vencido")
        self.assertEqual(respuesta.data["dias_restantes"], -3)
        self.assertEqual(respuesta.data["multa"], "6.00")

    def test_listado_de_vencidos_solo_para_personal(self):
        hoy = timezone.localdate()
        self.prestamo_directo(fecha_prestamo=hoy - timedelta(days=30), fecha_devolucion=hoy - timedelta(days=5))
        self.client.force_authenticate(self.estudiante)
        self.assertEqual(self.client.get("/api/prestamos/vencidos/").status_code, 403)
        self.client.force_authenticate(self.bibliotecario)
        respuesta = self.client.get("/api/prestamos/vencidos/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["count"], 1)

    def test_cada_usuario_ve_solo_sus_prestamos(self):
        self.prestamo_directo()
        self.client.force_authenticate(self.otro)
        self.assertEqual(self.client.get("/api/prestamos/").data["count"], 0)
        self.client.force_authenticate(self.estudiante)
        self.assertEqual(self.client.get("/api/prestamos/").data["count"], 1)