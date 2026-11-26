from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view

from carrito.serializers import CarritoSerializer
from carrito.views import CarritoViewSet
from ordenes.serializers import EstadoOrdenSerializer, OrdenSerializer
from ordenes.views import OrdenViewSet
from productos.views import ProductoViewSet
from resenas.views import ResenaViewSet
from usuarios.views import VendedorViewSet


def pedido(valor):
    return OpenApiExample('Request', value=valor, request_only=True)


def respuesta(valor, codigo='200'):
    return OpenApiExample('Response', value=valor, response_only=True, status_codes=[codigo])


def doc(*ejemplos, **opciones):
    return extend_schema(examples=list(ejemplos), **opciones)


PRODUCTO = {'id': 1, 'sku': 'TM-0001', 'nombre': 'Galaxy A55 Dell', 'marca': 'Dell', 'precio': '1500.00',
            'descuento': 10, 'precio_con_descuento': '1350.00', 'stock': 8, 'disponible': True, 'rating_promedio': 4.5}
NUEVO = {'sku': 'TM-0500', 'nombre': 'Laptop Pro', 'descripcion': 'Equipo de 16 GB', 'marca': 'Dell',
         'categoria_id': 1, 'precio': '3200.00', 'stock': 5}
CARRITO = {'id': 1, 'usuario': 'cliente1', 'cantidad_items': 1, 'subtotal': '1350.00', 'impuestos': '243.00',
           'total': '1593.00', 'total_con_descuento': '1274.40'}
ITEM = {'producto_id': 1, 'cantidad': 1, 'cupon': 'CYBER20'}
ENVIO = {'direccion_envio': 'Av. Giraldez 450, Huancayo', 'metodo_pago': 'culqi'}
ORDEN = {'id': 121, 'usuario': 'cliente1', 'estado': 'pendiente', 'total': '1274.40', 'numero_seguimiento': ''}
RESENA = {'producto': 1, 'calificacion': 5, 'titulo': 'Excelente', 'comentario': 'Buen equipo'}
VENDEDOR = {'id': 2, 'username': 'vendedor1', 'first_name': 'Ana', 'last_name': 'Rojas'}

extend_schema_view(
    list=doc(respuesta(PRODUCTO)),
    retrieve=doc(respuesta(PRODUCTO)),
    create=doc(pedido(NUEVO), respuesta(PRODUCTO, '201')),
    update=doc(pedido(NUEVO), respuesta(PRODUCTO)),
    partial_update=doc(pedido({'stock': 20}), respuesta(PRODUCTO)),
    destroy=extend_schema(description='Solo administrador. Responde 204 sin contenido.'),
    resenas=doc(respuesta(RESENA)),
)(ProductoViewSet)

extend_schema_view(
    list=doc(respuesta(CARRITO), responses=CarritoSerializer),
    agregar=doc(pedido(ITEM), respuesta(CARRITO), responses=CarritoSerializer),
    actualizar=doc(pedido({'producto_id': 1, 'cantidad': 2}), respuesta(CARRITO), responses=CarritoSerializer),
    eliminar=doc(pedido({'producto_id': 1}), respuesta(CARRITO), responses=CarritoSerializer),
    vaciar=doc(respuesta(CARRITO), request=None, responses=CarritoSerializer),
    checkout=doc(pedido(ENVIO), respuesta(ORDEN, '201'), responses={201: OrdenSerializer}),
)(CarritoViewSet)

extend_schema_view(
    list=doc(respuesta(ORDEN)),
    retrieve=doc(respuesta(ORDEN)),
    create=doc(pedido(ENVIO), respuesta(ORDEN, '201')),
    partial_update=doc(pedido({'estado': 'enviada'}), respuesta({**ORDEN, 'estado': 'enviada'}),
                       request=EstadoOrdenSerializer, responses=OrdenSerializer),
    cancelar=doc(respuesta({**ORDEN, 'estado': 'cancelada'}), request=None),
    mis_ordenes=doc(respuesta(ORDEN)),
)(OrdenViewSet)

extend_schema_view(
    list=doc(respuesta(RESENA)),
    retrieve=doc(respuesta(RESENA)),
    create=doc(pedido(RESENA), respuesta(RESENA, '201')),
    destroy=extend_schema(description='Autor o administrador. Responde 204 sin contenido.'),
)(ResenaViewSet)

extend_schema_view(
    list=doc(respuesta(VENDEDOR)),
    retrieve=doc(respuesta(VENDEDOR)),
)(VendedorViewSet)
