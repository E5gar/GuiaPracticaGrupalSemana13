from rest_framework.test import APITestCase

from comun.pruebas import crear_usuario

from .models import Autor, Categoria, Libro


class LibroApiTests(APITestCase):
    def setUp(self):
        self.autor = Autor.objects.create(nombre="Autor Uno", nacionalidad="Peruana")
        self.ing = Categoria.objects.create(nombre="Ingeniería", slug="ingenieria")
        self.lit = Categoria.objects.create(nombre="Literatura", slug="literatura")
        self.nuevo("Algoritmos", 2021, 5, self.ing)
        self.nuevo("Novela antigua", 2015, 0, self.lit)
        self.nuevo("Redes modernas", 2023, 2, self.ing)
        self.estudiante = crear_usuario("estudiante", "estudiante")
        self.bibliotecario = crear_usuario("bibliotecario", "bibliotecario")
        self.admin = crear_usuario("admin", superusuario=True)

    def nuevo(self, titulo, anio, stock, categoria):
        return Libro.objects.create(
            isbn=titulo,
            titulo=titulo,
            autor=self.autor,
            editorial="UNCP",
            anio=anio,
            categoria=categoria,
            stock=stock,
            estante="A-1",
            piso=1,
        )

    def test_catalogo_es_publico(self):
        respuesta = self.client.get("/api/libros/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["count"], 3)

    def test_campos_calculados_y_anidados(self):
        respuesta = self.client.get("/api/libros/")
        libro = next(l for l in respuesta.data["results"] if l["titulo"] == "Novela antigua")
        self.assertFalse(libro["disponible"])
        self.assertEqual(libro["autor"]["nombre"], "Autor Uno")
        self.assertIn("/api/libros/", libro["url"])

    def test_filtra_por_categoria(self):
        respuesta = self.client.get("/api/libros/", {"categoria": "ingenieria"})
        self.assertEqual(respuesta.data["count"], 2)

    def test_filtra_por_anio(self):
        respuesta = self.client.get("/api/libros/", {"año__gte": 2020})
        self.assertEqual(respuesta.data["count"], 2)

    def test_filtra_por_disponibilidad(self):
        respuesta = self.client.get("/api/libros/", {"disponible": "true"})
        self.assertEqual(respuesta.data["count"], 2)

    def test_busqueda_por_titulo(self):
        respuesta = self.client.get("/api/libros/", {"search": "redes"})
        self.assertEqual(respuesta.data["count"], 1)

    def test_ordena_por_anio_descendente(self):
        respuesta = self.client.get("/api/libros/", {"ordering": "-año"})
        self.assertEqual(respuesta.data["results"][0]["anio"], 2023)

    def test_permisos_de_escritura(self):
        datos = {
            "isbn": "978-0-00",
            "titulo": "Nuevo",
            "autor_id": self.autor.pk,
            "editorial": "UNCP",
            "anio": 2024,
            "categoria": "ingenieria",
            "stock": 3,
            "estante": "A-2",
            "piso": 1,
        }
        self.client.force_authenticate(self.estudiante)
        self.assertEqual(self.client.post("/api/libros/", datos, format="json").status_code, 403)
        self.client.force_authenticate(self.bibliotecario)
        creado = self.client.post("/api/libros/", datos, format="json")
        self.assertEqual(creado.status_code, 201)
        self.assertEqual(self.client.delete(f"/api/libros/{creado.data['id']}/").status_code, 403)
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.delete(f"/api/libros/{creado.data['id']}/").status_code, 204)