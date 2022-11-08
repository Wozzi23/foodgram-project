import django_filters

from recipes.models import Recipes


class RecipesFilters(django_filters.rest_framework.FilterSet):
    """
    Класс фильтрации полей модели Recipes для RecipesViewSet
    """
    tags = django_filters.rest_framework.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    author = django_filters.rest_framework.AllValuesFilter(
        field_name='author__id',
    )

    class Meta:
        model = Recipes
        fields = [
            'tags',
            'author',
        ]