from djoser.views import UserViewSet
from rest_framework import viewsets, filters

from api.paginations import CustomPageNumberPagination
from api.serializers import IngredientsSerializer
from recipes.models import Ingredients


class BaseUserViewSet(UserViewSet):
    """
    Убраны едпоинты Djoser которые не используется
    в данной версии проекта. При дальнейшей реализации
    методы будут удаляться. В соотвествии с требованиями
    проекта методы delete, pach, put убраны из разрешенных
    методов при расширении функционала не заыть добавить
    методы в разрешенные
    """
    pagination_class = CustomPageNumberPagination
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

    def _allowed_methods(self):
        return [m.upper() for m in self.http_method_names if hasattr(self, m)]

    def reset_username_confirm(self, request, *args, **kwargs):
        pass

    def reset_username(self, request, *args, **kwargs):
        pass

    def set_username(self, request, *args, **kwargs):
        pass

    def reset_password_confirm(self, request, *args, **kwargs):
        pass

    def reset_password(self, request, *args, **kwargs):
        pass

    def resend_activation(self, request, *args, **kwargs):
        pass

    def activation(self, request, *args, **kwargs):
        pass


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['^name', ]
    pagination_class = None
