from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """
    Класс изменяющий поле page_size модели PageNumberPagination на limit.
    """
    page_size_query_param = 'limit'
