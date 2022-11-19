from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """
    Кастомизация стандартной модели паджинации LimitOffsetPagination
    изменено поле offset на page. Стандартная настройка на уровне проекта
    'PAGE_SIZE': 10, если необходимо переопределить параметр в
    соответствии с потребностями.
    """
    page_size_query_param = 'limit'
