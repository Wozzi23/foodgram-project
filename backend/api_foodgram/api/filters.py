import django_filters

from recipes.models import Recipes


class RecipesFilters(django_filters.rest_framework.FilterSet):
    """
    Класс фильтрации полей модели Recipes для RecipesViewSet.
    tags, author - фильтруют запрос от любого пользователя,
    поля is_favorited и is_in_shopping_cart доступны только
    авторизованным пользователям.
    """
    tags = django_filters.rest_framework.AllValuesMultipleFilter(
        field_name='tags__slug', label='Теги'
    )
    author = django_filters.rest_framework.AllValuesFilter(
        field_name='author__id', label='Идентификатор автора'
    )
    is_favorited = django_filters.rest_framework.BooleanFilter(
        method='filter_is_favorited', label='Избранные'
    )
    is_in_shopping_cart = django_filters.rest_framework.BooleanFilter(
        method='filter_is_in_shopping_cart', label='В корзине'
    )

    def __boolean_filter(self, queryset, key):
        filter_for_user = {
            f'{key}__user': self.request.user
        }
        return queryset.filter(**filter_for_user)

    def filter_is_favorited(self, queryset, name, value):
        """
        Метод фильтрации по связанному полю модели Recipes с
        моделью FavoriteRecipes по полю user - пользователь
        от которого поступил запрос. Для корректной фильтрации
        требуется авторизация.
        """
        if value and self.request.user.is_authenticated:
            return self.__boolean_filter(queryset, 'favoriterecipes')
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """
        Метод фильтрации по связанному полю модели Recipes с
        моделью ShoppingCart по полю user - пользователь
        от которого поступил запрос. Для корректной фильтрации
        требуется авторизация.
        """
        if value and self.request.user.is_authenticated:
            return self.__boolean_filter(queryset, 'shoppingcart')
        return queryset

    class Meta:
        model = Recipes
        fields = [
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        ]
