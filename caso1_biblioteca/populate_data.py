import os
import random
from datetime import timedelta

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from libros.models import Autor, Categoria, Libro
from prestamos.models import Prestamo

User = get_user_model()
CLAVE = "Uncp2026!"

CATEGORIAS = [
    ("Programación", "programacion"),
    ("Ingeniería", "ingenieria"),
    ("Matemáticas", "matematicas"),
    ("Ciencias", "ciencias"),
    ("Literatura", "literatura"),
    ("Economía", "economia"),
    ("Historia", "historia"),
]

AUTORES = {
    "cormen": ("Thomas H. Cormen", "Estadounidense", "Profesor de ciencias de la computación en Dartmouth College y coautor de Introduction to Algorithms."),
    "martin": ("Robert C. Martin", "Estadounidense", "Ingeniero de software y consultor, conocido como Uncle Bob y firmante del Manifiesto Ágil."),
    "kernighan": ("Brian W. Kernighan", "Canadiense", "Científico de la computación ligado a los laboratorios Bell y a Princeton, coautor de El lenguaje de programación C."),
    "knuth": ("Donald E. Knuth", "Estadounidense", "Profesor emérito de Stanford, autor de The Art of Computer Programming y creador de TeX."),
    "fowler": ("Martin Fowler", "Británico", "Ingeniero de software y divulgador, autor de textos sobre refactorización y arquitectura empresarial."),
    "evans": ("Eric Evans", "Estadounidense", "Consultor de software, impulsor del diseño guiado por el dominio."),
    "tanenbaum": ("Andrew S. Tanenbaum", "Neerlandés", "Profesor emérito de la Vrije Universiteit de Ámsterdam y creador de MINIX."),
    "silberschatz": ("Abraham Silberschatz", "Estadounidense", "Profesor de ciencias de la computación en Yale, coautor de textos de sistemas operativos y bases de datos."),
    "russell": ("Stuart Russell", "Británico", "Profesor de ciencias de la computación en la Universidad de California, Berkeley, especialista en inteligencia artificial."),
    "norvig": ("Peter Norvig", "Estadounidense", "Investigador en inteligencia artificial y coautor de Artificial Intelligence: A Modern Approach."),
    "sommerville": ("Ian Sommerville", "Británico", "Académico de la ingeniería de software y autor del manual Software Engineering."),
    "pressman": ("Roger S. Pressman", "Estadounidense", "Consultor y autor de textos de ingeniería de software."),
    "garcia": ("Gabriel García Márquez", "Colombiano", "Escritor, Premio Nobel de Literatura 1982 y figura central del realismo mágico."),
    "vargas": ("Mario Vargas Llosa", "Peruano", "Escritor peruano, Premio Nobel de Literatura 2010."),
    "arguedas": ("José María Arguedas", "Peruano", "Escritor, antropólogo y etnólogo (1911-1969), narrador del mundo andino."),
    "palma": ("Ricardo Palma", "Peruano", "Escritor (1833-1919) y creador del género de las tradiciones peruanas."),
    "vallejo": ("César Vallejo", "Peruano", "Poeta (1892-1938) que renovó la poesía en lengua española."),
    "hawking": ("Stephen Hawking", "Británico", "Físico teórico (1942-2018), reconocido por sus trabajos sobre agujeros negros y cosmología."),
    "sagan": ("Carl Sagan", "Estadounidense", "Astrónomo y divulgador científico (1934-1996)."),
    "stewart": ("James Stewart", "Canadiense", "Matemático (1941-2014), autor de populares textos de cálculo."),
    "strang": ("Gilbert Strang", "Estadounidense", "Profesor de matemáticas del MIT y referente en álgebra lineal."),
    "kreyszig": ("Erwin Kreyszig", "Alemán", "Matemático (1922-2008), autor de Advanced Engineering Mathematics."),
    "kotler": ("Philip Kotler", "Estadounidense", "Economista y profesor, referente mundial del marketing."),
    "mankiw": ("N. Gregory Mankiw", "Estadounidense", "Economista y profesor de Harvard."),
    "harari": ("Yuval Noah Harari", "Israelí", "Historiador y profesor de la Universidad Hebrea de Jerusalén."),
}

LIBROS = [
    ("Introduction to Algorithms", "cormen", "MIT Press", 2022, "programacion"),
    ("Clean Code", "martin", "Prentice Hall", 2008, "programacion"),
    ("The Clean Coder", "martin", "Prentice Hall", 2011, "programacion"),
    ("Clean Architecture", "martin", "Pearson", 2017, "programacion"),
    ("The C Programming Language", "kernighan", "Prentice Hall", 1988, "programacion"),
    ("The Art of Computer Programming, Vol. 1", "knuth", "Addison-Wesley", 1997, "programacion"),
    ("The Art of Computer Programming, Vol. 2", "knuth", "Addison-Wesley", 1997, "programacion"),
    ("Refactoring", "fowler", "Addison-Wesley", 2018, "programacion"),
    ("Domain-Driven Design", "evans", "Addison-Wesley", 2003, "programacion"),
    ("Patterns of Enterprise Application Architecture", "fowler", "Addison-Wesley", 2002, "programacion"),
    ("The Unix Programming Environment", "kernighan", "Prentice Hall", 1984, "programacion"),
    ("Modern Operating Systems", "tanenbaum", "Pearson", 2014, "ingenieria"),
    ("Computer Networks", "tanenbaum", "Pearson", 2011, "ingenieria"),
    ("Structured Computer Organization", "tanenbaum", "Pearson", 2012, "ingenieria"),
    ("Distributed Systems", "tanenbaum", "Pearson", 2017, "ingenieria"),
    ("Operating System Concepts", "silberschatz", "Wiley", 2018, "ingenieria"),
    ("Database System Concepts", "silberschatz", "McGraw-Hill", 2019, "ingenieria"),
    ("Artificial Intelligence: A Modern Approach", "russell", "Pearson", 2020, "ingenieria"),
    ("Human Compatible", "russell", "Viking", 2019, "ingenieria"),
    ("Paradigms of AI Programming", "norvig", "Morgan Kaufmann", 1992, "ingenieria"),
    ("Software Engineering", "sommerville", "Pearson", 2016, "ingenieria"),
    ("Ingeniería de Software", "sommerville", "Pearson", 2011, "ingenieria"),
    ("Ingeniería del software: un enfoque práctico", "pressman", "McGraw-Hill", 2010, "ingenieria"),
    ("Software Engineering: A Practitioner's Approach", "pressman", "McGraw-Hill", 2019, "ingenieria"),
    ("Cálculo de una variable", "stewart", "Cengage", 2018, "matematicas"),
    ("Cálculo de varias variables", "stewart", "Cengage", 2018, "matematicas"),
    ("Cálculo: trascendentes tempranas", "stewart", "Cengage", 2012, "matematicas"),
    ("Introduction to Linear Algebra", "strang", "Wellesley-Cambridge Press", 2016, "matematicas"),
    ("Linear Algebra and Its Applications", "strang", "Cengage", 2005, "matematicas"),
    ("Calculus", "strang", "Wellesley-Cambridge Press", 2017, "matematicas"),
    ("Matemáticas avanzadas para ingeniería", "kreyszig", "Limusa Wiley", 2012, "matematicas"),
    ("Advanced Engineering Mathematics", "kreyszig", "Wiley", 2011, "matematicas"),
    ("Introductory Functional Analysis with Applications", "kreyszig", "Wiley", 1989, "matematicas"),
    ("Breve historia del tiempo", "hawking", "Crítica", 2011, "ciencias"),
    ("El universo en una cáscara de nuez", "hawking", "Crítica", 2002, "ciencias"),
    ("Agujeros negros y pequeños universos", "hawking", "Crítica", 1994, "ciencias"),
    ("Cosmos", "sagan", "Planeta", 2004, "ciencias"),
    ("El mundo y sus demonios", "sagan", "Planeta", 1997, "ciencias"),
    ("Contacto", "sagan", "Planeta", 1985, "ciencias"),
    ("Cien años de soledad", "garcia", "Sudamericana", 1967, "literatura"),
    ("El coronel no tiene quien le escriba", "garcia", "Era", 1961, "literatura"),
    ("Crónica de una muerte anunciada", "garcia", "La Oveja Negra", 1981, "literatura"),
    ("La ciudad y los perros", "vargas", "Seix Barral", 1963, "literatura"),
    ("Conversación en La Catedral", "vargas", "Seix Barral", 1969, "literatura"),
    ("La fiesta del Chivo", "vargas", "Alfaguara", 2000, "literatura"),
    ("Los ríos profundos", "arguedas", "Losada", 1958, "literatura"),
    ("Todas las sangres", "arguedas", "Losada", 1964, "literatura"),
    ("Tradiciones peruanas", "palma", "Espasa Calpe", 1953, "literatura"),
    ("Trilce", "vallejo", "Talleres de la Penitenciaría", 1922, "literatura"),
    ("Fundamentos de marketing", "kotler", "Pearson", 2017, "economia"),
    ("Dirección de marketing", "kotler", "Pearson", 2016, "economia"),
    ("Principios de economía", "mankiw", "Cengage", 2017, "economia"),
    ("Macroeconomía", "mankiw", "Antoni Bosch", 2014, "economia"),
    ("Sapiens: de animales a dioses", "harari", "Debate", 2014, "historia"),
    ("Homo Deus", "harari", "Debate", 2016, "historia"),
    ("21 lecciones para el siglo XXI", "harari", "Debate", 2018, "historia"),
]

PERSONAL = [
    ("admin.biblioteca", "Rosa", "Quispe Mayta", "administrador", ""),
    ("bib.camila", "Camila", "Rojas Yauri", "bibliotecario", ""),
    ("bib.jorge", "Jorge", "Huamán Ccora", "bibliotecario", ""),
]

LECTORES = [
    ("lucia.ramos", "Lucía", "Ramos Poma", "estudiante", "Ingeniería de Sistemas"),
    ("diego.vilcapoma", "Diego", "Vilcapoma Soto", "estudiante", "Ingeniería Civil"),
    ("karen.mendoza", "Karen", "Mendoza Arroyo", "estudiante", "Ingeniería Industrial"),
    ("miguel.lazo", "Miguel", "Lazo Cárdenas", "estudiante", "Ingeniería de Sistemas"),
    ("andrea.huaman", "Andrea", "Huamán Tapia", "estudiante", "Ingeniería Eléctrica y Electrónica"),
    ("renzo.ccanto", "Renzo", "Ccanto Llacza", "estudiante", "Ingeniería de Minas"),
    ("yesenia.paucar", "Yesenia", "Paucar Vila", "estudiante", "Ingeniería Química"),
    ("bruno.zevallos", "Bruno", "Zevallos Inga", "estudiante", "Ingeniería Ambiental"),
    ("dr.alarcon", "Walter", "Alarcón Baldeón", "docente", "Ingeniería de Sistemas"),
    ("mg.santivanez", "Elena", "Santivañez Cóndor", "docente", "Ingeniería Civil"),
    ("inv.palomino", "Héctor", "Palomino Rivas", "investigador", "Ingeniería de Sistemas"),
]


def crear_usuarios():
    creados = []
    for i, (username, nombre, apellidos, tipo, carrera) in enumerate(PERSONAL + LECTORES):
        correo = f"{username}@uncp.edu.pe"
        if tipo == "administrador":
            usuario = User.objects.create_superuser(username, correo, CLAVE, first_name=nombre, last_name=apellidos)
        else:
            usuario = User.objects.create_user(username, correo, CLAVE, first_name=nombre, last_name=apellidos)
        perfil = usuario.perfil
        perfil.tipo = tipo
        perfil.carrera = carrera
        perfil.telefono = "9" + "".join(str(random.randint(0, 9)) for _ in range(8))
        perfil.carnet = "" if tipo in ("administrador", "bibliotecario") else f"{random.randint(2019, 2025)}{i:05d}"
        perfil.save()
        creados.append(usuario)
    return creados


def crear_catalogo():
    categorias = {slug: Categoria.objects.create(nombre=nombre, slug=slug) for nombre, slug in CATEGORIAS}
    autores = {clave: Autor.objects.create(nombre=n, nacionalidad=nac, biografia=bio) for clave, (n, nac, bio) in AUTORES.items()}
    letras = {slug: chr(65 + i) for i, (_, slug) in enumerate(CATEGORIAS)}
    pisos = {slug: i % 3 + 1 for i, (_, slug) in enumerate(CATEGORIAS)}
    libros = []
    for i, (titulo, autor, editorial, anio, slug) in enumerate(LIBROS, start=1):
        libros.append(
            Libro.objects.create(
                isbn=f"978-9972-{i:04d}-{(i * 7) % 10}",
                titulo=titulo,
                autor=autores[autor],
                editorial=editorial,
                anio=anio,
                categoria=categorias[slug],
                stock=random.randint(3, 8),
                estante=f"{letras[slug]}-{random.randint(1, 40)}",
                piso=pisos[slug],
                portada=f"https://picsum.photos/seed/libro{i}/400/560",
            )
        )
    return libros


def crear_prestamos(lectores, libros):
    hoy = timezone.localdate()

    def con_stock():
        return random.choice([l for l in libros if l.stock > 0])

    def abrir(lector, dias_atras, estado):
        libro = con_stock()
        libro.stock -= 1
        libro.save(update_fields=["stock"])
        inicio = hoy - timedelta(days=dias_atras)
        Prestamo.objects.create(
            usuario=lector,
            libro=libro,
            fecha_prestamo=inicio,
            fecha_devolucion=inicio + timedelta(days=Prestamo.DIAS_PRESTAMO),
            estado=estado,
        )

    for _ in range(14):
        libro = random.choice(libros)
        inicio = hoy - timedelta(days=random.randint(30, 120))
        Prestamo.objects.create(
            usuario=random.choice(lectores),
            libro=libro,
            fecha_prestamo=inicio,
            fecha_devolucion=inicio + timedelta(days=Prestamo.DIAS_PRESTAMO),
            fecha_devuelto=inicio + timedelta(days=random.randint(5, 22)),
            estado=Prestamo.DEVUELTO,
        )

    for _ in range(5):
        abrir(lectores[0], random.randint(0, 10), Prestamo.ACTIVO)
    for i in range(9):
        abrir(lectores[1 + i % (len(lectores) - 1)], random.randint(0, 10), Prestamo.ACTIVO)
    for i in range(8):
        abrir(lectores[1 + i % (len(lectores) - 1)], random.randint(20, 45), Prestamo.VENCIDO)

    for libro in random.sample(libros, 7):
        libro.stock = 0
        libro.save(update_fields=["stock"])


@transaction.atomic
def main():
    random.seed(93)
    Prestamo.objects.all().delete()
    Libro.objects.all().delete()
    Autor.objects.all().delete()
    Categoria.objects.all().delete()
    User.objects.all().delete()

    usuarios = crear_usuarios()
    libros = crear_catalogo()
    lectores = usuarios[len(PERSONAL):]
    crear_prestamos(lectores, libros)

    print(f"Libros: {Libro.objects.count()}")
    print(f"Usuarios: {User.objects.count()}")
    print(f"Préstamos: {Prestamo.objects.count()}")
    print(f"Contraseña de todos los usuarios: {CLAVE}")
    print("Administrador: admin.biblioteca | Bibliotecarios: bib.camila, bib.jorge")
    print("Con cupo lleno (5 préstamos): lucia.ramos")


if __name__ == "__main__":
    main()