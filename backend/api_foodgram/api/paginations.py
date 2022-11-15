from rest_framework.pagination import LimitOffsetPagination


class CustomLimitOffsetPagination(LimitOffsetPagination):
    """
    Кастомизация стандартной модели паджинации LimitOffsetPagination
    изменено поле offset на page. Стандартная настройка на уровне проекта
    'PAGE_SIZE': 10, если необходимо переопределить параметр в
    соответствии с потребностями.
    """
    offset_query_param = 'page'
