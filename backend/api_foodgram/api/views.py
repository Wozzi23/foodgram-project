import io

from django.db.models import Count
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.pdfgen import canvas
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import RecipesFilters
from api.paginations import CustomLimitOffsetPagination
from api.permissions import ReadAnyOrAuthorOnly
from api.serializers import IngredientsSerializer, TagsSerializer, RecipesSerializer, RecipeMinifiedSerializer, \
    SubscriptionsSerializer
from recipes.models import Ingredients, Tags, Recipes, FavoriteRecipes, ShoppingCart, IngredientInRecipe
from users.models import Subscriptions, User


class BaseUserViewSet(UserViewSet):
    """
    Убраны едпоинты Djoser которые не используется
    в данной версии проекта. При дальнейшей реализации
    методы будут удаляться. В соотвествии с требованиями
    проекта методы delete, pach, put убраны из разрешенных
    методов при расширении функционала не заыть добавить
    методы в разрешенные.
    """
    pagination_class = CustomLimitOffsetPagination
    http_method_names = ['get', 'post', 'head', 'options', 'trace']

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

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='subscriptions',
    )
    def get_subscriptions_list(self, request):
        """
        Функция обработки GET запроса subscriptions
        """
        subscriptions = (
            User.objects.filter(subscribe_author__user=self.request.user).
            prefetch_related('recipes').
            annotate(recipes_count=Count('recipes'))
        )
        page = self.paginate_queryset(subscriptions)
        serializer = SubscriptionsSerializer(
            context={'request': self.request},
            data=page,
            many=True
        )
        serializer.is_valid()
        return self.get_paginated_response(serializer.data)


class SubscribeAPI(APIView):
    """
    Класс обработки POST и DELETE запроса
    subscribe, достпно только авторизованным пользователям.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, id):
        if request.method == 'POST':
            author = get_object_or_404(User, id=id)
            sub, create = Subscriptions.objects.get_or_create(user=self.request.user, author=author)
            a2 = User.objects.filter(id=id).prefetch_related('recipes').annotate(recipes_count=Count('recipes'))
            if create:
                serializer = SubscriptionsSerializer(a2.first(),
                                                     context={'request': self.request}, )
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            else:
                return Response({'errors': 'Вы уже подписаны на данного автора'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        author = get_object_or_404(User, id=id)
        subscribe = Subscriptions.objects.filter(user=self.request.user, author=author)
        if subscribe.exists():
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'errors': 'Вы не подписанны на этого автора'}, status=status.HTTP_400_BAD_REQUEST)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Класс обработки GET запроса Ingredients,
    достпно всем пользователям. Реализован поиск
    по названию тега.
    """

    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['^name', ]
    pagination_class = None


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Класс обработки GET запроса Tags,
    достпно всем пользователям.
    """

    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


def favorite_recipe2(self, request, pk, model):
    """
    Базовая функция для favorite и shopping_cart,
    так как методы схожи реализована одна функция для 2 запросов
    для корректной обратотки необходимо передавать модель в запрос
    """
    recipe = get_object_or_404(Recipes, id=pk)
    user = self.request.user
    if request.method == 'POST':
        favorite_recipes, create = model.objects.get_or_create(user=user, recipe=recipe)
        if create:
            return Response(RecipeMinifiedSerializer(recipe).data, status=status.HTTP_201_CREATED)
        else:
            return Response({'errors': 'Рецепт уже добален'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        favorite_recipes = model.objects.filter(user=user, recipe=recipe)
        if favorite_recipes.exists():
            favorite_recipes.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'errors': 'Рецепт не был добален'}, status=status.HTTP_400_BAD_REQUEST)


class RecipesViewSet(viewsets.ModelViewSet):
    """
    Класс обработки выдачи рецептов. Исключен метод PUT из разрешенных
    для соответвия техзаданию. Реализована паджинация и фильтрация полей
    """
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    pagination_class = CustomLimitOffsetPagination
    permission_classes = (ReadAnyOrAuthorOnly,)
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RecipesFilters
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options', 'trace']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path='favorite',
    )
    def favorite_recipe(self, request, pk):
        """
        Функция добавления/удаления рецепта из избранного.
        """
        return favorite_recipe2(self, request, pk, FavoriteRecipes)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path='shopping_cart',
    )
    def shopping_cart(self, request, pk):
        """
        Функция добавления/удаления рецепта из списка покупок.
        """
        return favorite_recipe2(self, request, pk, ShoppingCart)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        """
        Функция выдает PDF файл со списком покупок, реализована проверка
        на совпаление ингридиентов и в случае совпадения суммирует поле
        amount.
        """
        ing = IngredientInRecipe.objects.filter(recipe__shoppingcart__user=self.request.user)
        res = {}
        for i in ing:
            value = res.get(i.ingredient.name)
            if value is not None:
                value[1] += i.amount
            else:
                res.update({i.ingredient.name: [i.ingredient.measurement_unit, i.amount]})
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        my_font_object = ttfonts.TTFont('Arial', 'arial.ttf')
        pdfmetrics.registerFont(my_font_object)
        p.setFont('Arial', 24)
        p.drawString(100, 700, 'Список покупок:')
        p.setFont('Arial', 14)
        x = 680
        num = 1
        for key, val in res.items():
            p.drawString(120, x, f'{num}. {key} {val[1]} {val[0]}')
            x -= 20
            num += 1
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='hello.pdf')
