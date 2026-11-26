from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination


class PaginacionEstandar(PageNumberPagination):
    page_size = 20
    page_size_query_param = "tamano"
    max_page_size = 100


class PaginacionLimitOffset(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100