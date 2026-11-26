import os
import random
from datetime import timedelta
from decimal import Decimal

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from carrito.models import Carrito, ItemCarrito
from ordenes.models import ItemOrden, Orden
from productos.models import Categoria, ImagenProducto, Marca, Producto
from resenas.models import Resena
from usuarios.models import PerfilUsuario

CLAVE = 'Tecno2026*'

CATALOGO = {
    'Laptops': (['Inspiron 15', 'IdeaPad 5', 'Pavilion 14', 'VivoBook 16', 'Aspire 7'], 1800, 6500),
    'Smartphones': (['Galaxy A55', 'Redmi Note 13', 'Moto G84', 'iPhone 15', 'Pixel 8'], 700, 4200),
    'Componentes': (['SSD NVMe 1TB', 'Memoria DDR5 16GB', 'Fuente 650W', 'Placa B760', 'RTX 4060'], 150, 1900),
    'Accesorios': (['Mouse inalambrico', 'Teclado mecanico', 'Audifonos Bluetooth', 'Webcam HD', 'Hub USB-C'], 35, 450),
}
MARCAS = ['Dell', 'Lenovo', 'HP', 'Asus', 'Acer', 'Samsung', 'Xiaomi', 'Motorola', 'Logitech', 'Kingston']
NOMBRES = ['Ana', 'Luis', 'Maria', 'Carlos', 'Rosa', 'Jorge', 'Lucia', 'Pedro', 'Elena', 'Diego']
APELLIDOS = ['Quispe', 'Huaman', 'Rojas', 'Flores', 'Mendoza', 'Torres', 'Vargas', 'Castro']
DIRECCIONES = ['Av. Giraldez 450, Huancayo', 'Jr. Puno 230, Huancayo', 'Av. Arequipa 1200, Lima', 'Calle Real 980, El Tambo']
OPINIONES = {
    1: ('No lo recomiendo', 'Llego con fallas y tuve que pedir cambio.'),
    2: ('Regular tirando a malo', 'Esperaba mejor calidad por el precio.'),
    3: ('Cumple lo basico', 'Funciona bien, sin nada especial.'),
    4: ('Buena compra', 'Buen rendimiento y llego a tiempo.'),
    5: ('Excelente', 'Supero mis expectativas, volveria a comprar.'),
}


def crear_usuario(username, rol, **extra):
    usuario = User.objects.create_user(
        username=username,
        password=CLAVE,
        email=f'{username}@tecnomarket.pe',
        first_name=random.choice(NOMBRES),
        last_name=random.choice(APELLIDOS),
        **extra,
    )
    PerfilUsuario.objects.create(usuario=usuario, rol=rol, telefono=f'9{random.randint(10000000, 99999999)}')
    return usuario


def limpiar():
    Orden.objects.all().delete()
    Resena.objects.all().delete()
    Carrito.objects.all().delete()
    Producto.objects.all().delete()
    Categoria.objects.all().delete()
    Marca.objects.all().delete()
    User.objects.filter(email__endswith='@tecnomarket.pe').delete()


@transaction.atomic
def poblar():
    random.seed(13)
    limpiar()

    crear_usuario('admin', PerfilUsuario.Rol.ADMIN, is_staff=True, is_superuser=True)
    vendedores = [crear_usuario(f'vendedor{i}', PerfilUsuario.Rol.VENDEDOR) for i in range(1, 5)]
    clientes = [crear_usuario(f'cliente{i}', PerfilUsuario.Rol.CLIENTE) for i in range(1, 21)]

    marcas = [Marca.objects.create(nombre=nombre) for nombre in MARCAS]
    categorias = {
        nombre: Categoria.objects.create(
            nombre=nombre,
            descripcion=f'{nombre} disponibles en TecnoMarket Peru',
            imagen=f'https://picsum.photos/seed/{nombre.lower()}/600/400',
        )
        for nombre in CATALOGO
    }

    productos = []
    for i in range(1, 121):
        nombre_categoria = list(CATALOGO)[i % len(CATALOGO)]
        modelos, minimo, maximo = CATALOGO[nombre_categoria]
        marca = random.choice(marcas)
        modelo = random.choice(modelos)
        producto = Producto.objects.create(
            sku=f'TM-{i:04d}',
            nombre=f'{modelo} {marca.nombre}',
            descripcion=f'{modelo} de la marca {marca.nombre} con garantia de 12 meses',
            marca=marca,
            categoria=categorias[nombre_categoria],
            precio=Decimal(random.randint(minimo, maximo)),
            descuento=random.choice([0, 0, 0, 10, 15, 25]),
            stock=0 if i % 12 == 0 else random.randint(3, 60),
            vendedor=random.choice(vendedores),
            especificaciones={'garantia_meses': 12, 'color': random.choice(['negro', 'plata', 'azul'])},
            fecha_creacion=timezone.now() - timedelta(days=random.randint(0, 180)),
        )
        for n in range(1, 3):
            ImagenProducto.objects.create(producto=producto, url=f'https://picsum.photos/seed/{producto.sku}-{n}/600/600')
        productos.append(producto)

    comprados = []
    estados = list(Orden.Estado.values)
    for i in range(60):
        cliente = clientes[i % len(clientes)]
        estado = estados[i % len(estados)]
        orden = Orden.objects.create(
            usuario=cliente,
            direccion_envio=random.choice(DIRECCIONES),
            metodo_pago=random.choice(Orden.MetodoPago.values),
            estado=estado,
            fecha_creacion=timezone.now() - timedelta(days=random.randint(0, 90)),
        )
        total = 0
        for producto in random.sample(productos, 3):
            cantidad = random.randint(1, 3)
            item = ItemOrden.objects.create(
                orden=orden,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio_con_descuento,
            )
            total += item.importe
            if estado in ('pagada', 'enviada', 'entregada'):
                comprados.append((cliente, producto))
        orden.total = total
        orden.save()

    pares = list(dict.fromkeys(comprados))
    for cliente, producto in random.sample(pares, min(105, len(pares))):
        calificacion = random.choice([1, 2, 3, 4, 4, 5, 5, 5])
        titulo, comentario = OPINIONES[calificacion]
        Resena.objects.create(
            usuario=cliente,
            producto=producto,
            calificacion=calificacion,
            titulo=titulo,
            comentario=comentario,
        )

    for cliente in clientes[:5]:
        carrito = Carrito.objects.create(usuario=cliente)
        for producto in random.sample([p for p in productos if p.stock > 0], 2):
            ItemCarrito.objects.create(carrito=carrito, producto=producto, cantidad=1)


if __name__ == '__main__':
    poblar()
    print(f'Productos: {Producto.objects.count()}')
    print(f'Usuarios: {User.objects.count()}')
    print(f'Ordenes: {Orden.objects.count()}')
    print(f'Resenas: {Resena.objects.count()}')
