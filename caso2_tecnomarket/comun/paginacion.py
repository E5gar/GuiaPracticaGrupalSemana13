from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination


class PaginacionProductos(PageNumberPagination):
    page_size = 24


class PaginacionOrdenes(LimitOffsetPagination):
    default_limit = 50
    max_limit = 50
