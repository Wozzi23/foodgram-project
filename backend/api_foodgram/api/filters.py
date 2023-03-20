import django_filters

from recipes.models import Recipes


class RecipesFilters(django_filters.rest_framework.FilterSet):
    """
    Класс фильтрации полей модели Recipes для RecipesViewSet.

    '''
    Атрибуты
    --------
    tags: str
        теги
    author: int
        id автора
    is_favorited: bool
        в избранном
    is_in_shopping_cart: bool
        в корзине

    Методы
    ------
    filter_is_favorited(queryset, name, value):
        Фильтрует рецепты по находящимся в избранном у пользователя

    filter_is_in_shopping_cart(queryset, name, value):
        Фильтрует рецепты по находящимся в списке покупок у пользователя
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

    def filter_is_favorited(self, queryset, name, value):
        """
        Возвращает queryset модели FavoriteRecipes отфильтрованный
        по пользователю сделавшему запрос

        Параметры
        ---------
        queryset: Queryset[list]
            список избранных рецептов
        value: bool
            значение переданное в запросе

        Возвращаемое значение
        ---------------------
        queryset: Queryset[list]
        """
        if value and self.request.user.is_authenticated:
            return queryset.filter(favoriterecipes__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """
        Возвращает queryset модели ShoppingCart отфильтрованный
        по пользователю сделавшему запрос

        Параметры
        ---------
        queryset: Queryset[list]
            список избранных рецептов
        value: bool
            значение переданное в запросе

        Возвращаемое значение
        ---------------------
        queryset: Queryset[list]
        """
        if value and self.request.user.is_authenticated:
            return queryset.filter(shoppingcart__user=self.request.user)
        return queryset

    class Meta:
        model = Recipes
        fields = [
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        ]
